"""Maps JSON HTTP create requests to address-context application commands."""

import json
from http import HTTPStatus
from typing import Any

from src.adapters.inbound.http.request import HttpRequest
from src.application.addresses.address_create_command import (
    AddressAssignmentPayloadCommand,
    AddressCreateCommand,
    AddressPayloadCommand,
    AddressUnitHierarchyPayloadCommand,
    AddressUnitPayloadCommand,
    BuildingPayloadCommand,
    CityPayloadCommand,
    GeoLocationCommand,
    RelatedEntityPayloadCommand,
    StreetPayloadCommand,
)


class AddressCreateHttpRequestError(ValueError):
    """Raised when an HTTP create request cannot be mapped to an application command."""

    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class AddressCreateHttpRequestMapper:
    """Converts JSON HTTP requests into address-context create commands."""

    def map(self, request: HttpRequest) -> AddressCreateCommand:
        """Validate transport input and create the application command."""
        _require_json_content_type(request)
        payload = _parse_json_payload(request.body)

        return AddressCreateCommand(
            address=_map_address_payload(_require_object_field(payload, "address")),
            street=_map_street_payload(_require_object_field(payload, "street")),
            city=_map_city_payload(_require_object_field(payload, "city")),
            building=_map_optional_building_payload(payload.get("building")),
            units=_map_units_payload(_require_optional_list_field(payload, "units")),
            unit_hierarchy=_map_unit_hierarchy_payload(
                _require_optional_list_field(payload, "unit_hierarchy")
            ),
            assignments=_map_assignments_payload(_require_optional_list_field(payload, "assignments")),
        )


def _require_json_content_type(request: HttpRequest) -> None:
    content_type = request.header("content-type")
    if content_type is None or not content_type.lower().startswith("application/json"):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            code="unsupported_media_type",
            message="Content-Type must be application/json",
        )


def _parse_json_payload(body: bytes) -> dict[str, object]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_json",
            message="Request body must contain valid JSON",
        ) from error

    if not isinstance(payload, dict):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_json",
            message="JSON payload must be an object",
        )

    return payload


def _map_address_payload(payload: dict[str, object]) -> AddressPayloadCommand:
    return AddressPayloadCommand(
        house_number=_require_string_field(payload, "house_number"),
        geo_location=_map_optional_geo_location_payload(payload.get("geo_location"), field_name="address.geo_location"),
    )


def _map_street_payload(payload: dict[str, object]) -> StreetPayloadCommand:
    return StreetPayloadCommand(name=_require_string_field(payload, "name"))


def _map_city_payload(payload: dict[str, object]) -> CityPayloadCommand:
    return CityPayloadCommand(
        name=_require_string_field(payload, "name"),
        country=_require_string_field(payload, "country"),
        postal_code=_require_optional_string_field(payload, "postal_code"),
    )


def _map_optional_building_payload(payload: object) -> BuildingPayloadCommand | None:
    if payload is None:
        return None

    building_payload = _require_object(payload, field_name="building")
    return BuildingPayloadCommand(
        name=_require_optional_string_field(building_payload, "name"),
        geo_location=_map_optional_geo_location_payload(
            building_payload.get("geo_location"),
            field_name="building.geo_location",
        ),
    )


def _map_units_payload(payload: list[object]) -> tuple[AddressUnitPayloadCommand, ...]:
    return tuple(
        AddressUnitPayloadCommand(
            unit_type=_require_string_field(_require_object(item, field_name=f"units[{index}]"), "unit_type"),
            value=_require_string_field(_require_object(item, field_name=f"units[{index}]"), "value"),
        )
        for index, item in enumerate(payload)
    )


def _map_unit_hierarchy_payload(
    payload: list[object],
) -> tuple[AddressUnitHierarchyPayloadCommand, ...]:
    return tuple(
        AddressUnitHierarchyPayloadCommand(
            parent_ref=_require_string_field(
                _require_object(item, field_name=f"unit_hierarchy[{index}]"),
                "parent_ref",
            ),
            child_ref=_require_string_field(
                _require_object(item, field_name=f"unit_hierarchy[{index}]"),
                "child_ref",
            ),
        )
        for index, item in enumerate(payload)
    )


def _map_assignments_payload(payload: list[object]) -> tuple[AddressAssignmentPayloadCommand, ...]:
    return tuple(
        _map_assignment_payload(_require_object(item, field_name=f"assignments[{index}]"))
        for index, item in enumerate(payload)
    )


def _map_assignment_payload(payload: dict[str, object]) -> AddressAssignmentPayloadCommand:
    return AddressAssignmentPayloadCommand(
        related_entity=_map_related_entity_payload(_require_object_field(payload, "related_entity")),
        relation_type=_require_string_field(payload, "relation_type"),
        valid_from=_require_optional_string_field(payload, "valid_from"),
        valid_to=_require_optional_string_field(payload, "valid_to"),
        source=_require_optional_string_field(payload, "source"),
        note=_require_optional_string_field(payload, "note"),
    )


def _map_related_entity_payload(payload: dict[str, object]) -> RelatedEntityPayloadCommand:
    return RelatedEntityPayloadCommand(
        entity_type=_require_string_field(payload, "entity_type"),
        entity_id=_require_string_field(payload, "entity_id"),
    )


def _map_optional_geo_location_payload(payload: object, *, field_name: str) -> GeoLocationCommand | None:
    if payload is None:
        return None

    geo_payload = _require_object(payload, field_name=field_name)
    return GeoLocationCommand(
        latitude=_require_numeric_field(geo_payload, "latitude", owner=field_name),
        longitude=_require_numeric_field(geo_payload, "longitude", owner=field_name),
    )


def _require_object_field(payload: dict[str, object], field_name: str) -> dict[str, object]:
    if field_name not in payload:
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="missing_required_field",
            message=f"Field '{field_name}' is required",
        )
    return _require_object(payload[field_name], field_name=field_name)


def _require_optional_list_field(payload: dict[str, object], field_name: str) -> list[object]:
    if field_name not in payload:
        return []
    field_value = payload[field_name]
    if not isinstance(field_value, list):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message=f"Field '{field_name}' must be an array",
        )
    return field_value


def _require_object(value: object, *, field_name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message=f"Field '{field_name}' must be an object",
        )
    return value


def _require_string_field(payload: dict[str, object], field_name: str) -> str:
    if field_name not in payload:
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="missing_required_field",
            message=f"Field '{field_name}' is required",
        )

    return _require_string(payload[field_name], field_name=field_name)


def _require_optional_string_field(payload: dict[str, object], field_name: str) -> str | None:
    if field_name not in payload or payload[field_name] is None:
        return None
    return _require_string(payload[field_name], field_name=field_name)


def _require_string(value: object, *, field_name: str) -> str:
    if not isinstance(value, str):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message=f"Field '{field_name}' must be a string",
        )
    return value


def _require_numeric_field(payload: dict[str, object], field_name: str, *, owner: str) -> float:
    if field_name not in payload:
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="missing_required_field",
            message=f"Field '{owner}.{field_name}' is required",
        )

    field_value = payload[field_name]
    if isinstance(field_value, bool) or not isinstance(field_value, (int, float)):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message=f"Field '{owner}.{field_name}' must be numeric",
        )

    return float(field_value)
