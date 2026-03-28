"""Maps JSON HTTP create requests to address application commands."""

import json
from http import HTTPStatus

from src.adapters.inbound.http.request import HttpRequest
from src.application.addresses.address_create_command import AddressCreateCommand


class AddressCreateHttpRequestError(ValueError):
    """Raised when an HTTP create request cannot be mapped to an application command."""

    def __init__(self, *, status_code: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message


class AddressCreateHttpRequestMapper:
    """Converts JSON HTTP requests into address create commands."""

    def map(self, request: HttpRequest) -> AddressCreateCommand:
        """Validate transport input and create the application command."""
        _require_json_content_type(request)
        payload = _parse_json_payload(request.body)
        latitude, longitude = _map_geo_location(payload.get("geo_location"))
        return AddressCreateCommand(
            house_number=_require_string_field(payload, "house_number"),
            latitude=latitude,
            longitude=longitude,
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


def _require_string_field(payload: dict[str, object], field_name: str) -> str:
    if field_name not in payload:
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="missing_required_field",
            message=f"Field '{field_name}' is required",
        )

    field_value = payload[field_name]
    if not isinstance(field_value, str):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message=f"Field '{field_name}' must be a string",
        )

    return field_value


def _map_geo_location(geo_location_payload: object) -> tuple[float | None, float | None]:
    return _GEO_LOCATION_PAYLOAD_MAPPERS.get(
        geo_location_payload is None,
        _map_present_geo_location,
    )(geo_location_payload)


def _map_missing_geo_location(geo_location_payload: object) -> tuple[float | None, float | None]:
    del geo_location_payload
    return None, None


def _map_present_geo_location(geo_location_payload: object) -> tuple[float | None, float | None]:
    if not isinstance(geo_location_payload, dict):
        raise AddressCreateHttpRequestError(
            status_code=HTTPStatus.BAD_REQUEST,
            code="invalid_field_type",
            message="Field 'geo_location' must be an object or null",
        )

    latitude = _require_numeric_field(geo_location_payload, "latitude", owner="geo_location")
    longitude = _require_numeric_field(geo_location_payload, "longitude", owner="geo_location")
    return float(latitude), float(longitude)


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


_GEO_LOCATION_PAYLOAD_MAPPERS = {
    True: _map_missing_geo_location,
    False: _map_present_geo_location,
}
