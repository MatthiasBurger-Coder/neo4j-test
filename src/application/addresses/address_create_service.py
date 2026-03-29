"""Application service for address-context create operations."""

import logging
from datetime import datetime

from src.application.addresses.address_context import (
    AddressContextAddressDraft,
    AddressContextAssignmentDraft,
    AddressContextBuildingDraft,
    AddressContextCityDraft,
    AddressContextDraft,
    AddressContextStreetDraft,
    AddressContextUnitDraft,
    AddressContextUnitHierarchyDraft,
    CreatedAddressContext,
)
from src.application.addresses.address_create_command import (
    AddressAssignmentPayloadCommand,
    AddressCreateCommand,
    AddressUnitHierarchyPayloadCommand,
    AddressUnitPayloadCommand,
    BuildingPayloadCommand,
    CityPayloadCommand,
    GeoLocationCommand,
)
from src.application.addresses.address_create_port import AddressCreatePort
from src.application.addresses.address_write_port import AddressWriteError, AddressWritePort
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef, RelatedEntityType
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_non_blank_text, require_optional_non_blank_text


class AddressCreateValidationError(ValueError):
    """Raised when address creation input violates domain constraints."""


class AddressCreateOperationError(RuntimeError):
    """Raised when address creation fails for technical reasons."""


class AddressCreateService(AddressCreatePort):
    """Coordinates address-context create use cases through the outbound write port."""

    def __init__(
        self,
        address_write_port: AddressWritePort,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self._address_write_port = address_write_port
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def create_address(self, command: AddressCreateCommand) -> CreatedAddressContext:
        """Validate the incoming command and delegate the write to the outbound port."""
        self._logger.info("Address create started | operation=create_address")

        try:
            address_context = AddressContextDraft(
                address=AddressContextAddressDraft(
                    house_number=require_non_blank_text(
                        owner="Address",
                        field_name="house_number",
                        value=command.address.house_number,
                    ),
                    geo_location=_map_geo_location(command.address.geo_location, owner="Address"),
                ),
                street=AddressContextStreetDraft(
                    name=require_non_blank_text(
                        owner="Street",
                        field_name="name",
                        value=command.street.name,
                    )
                ),
                city=_map_city(command.city),
                building=_map_building(command.building),
                units=_map_units(command.units),
                unit_hierarchy=_map_unit_hierarchy(command.unit_hierarchy),
                assignments=_map_assignments(command.assignments),
            )
            _validate_unit_hierarchy(address_context)
        except ValueError as error:
            self._logger.warning(
                "Address create rejected | operation=create_address | error=%s",
                error,
            )
            raise AddressCreateValidationError(str(error)) from error

        try:
            created_address_context = self._address_write_port.create_address(address_context)
        except AddressWriteError as error:
            self._logger.error(
                "Address create failed | operation=create_address | error=%s",
                error,
            )
            raise AddressCreateOperationError("Address context could not be created") from error

        self._logger.info(
            "Address create succeeded | operation=create_address | address_id=%s",
            created_address_context.address.id.value,
        )
        return created_address_context


def _map_geo_location(geo_location: GeoLocationCommand | None, *, owner: str) -> GeoLocation | None:
    if geo_location is None:
        return None
    return GeoLocation(latitude=geo_location.latitude, longitude=geo_location.longitude)


def _map_city(command: CityPayloadCommand) -> AddressContextCityDraft:
    return AddressContextCityDraft(
        name=require_non_blank_text(owner="City", field_name="name", value=command.name),
        country=require_non_blank_text(owner="City", field_name="country", value=command.country),
        postal_code=require_optional_non_blank_text(
            owner="City",
            field_name="postal_code",
            value=command.postal_code,
        ),
    )


def _map_building(command: BuildingPayloadCommand | None) -> AddressContextBuildingDraft | None:
    if command is None:
        return None

    building = AddressContextBuildingDraft(
        name=require_optional_non_blank_text(
            owner="Building",
            field_name="name",
            value=command.name,
        ),
        geo_location=_map_geo_location(command.geo_location, owner="Building"),
    )
    if building.name is None and building.geo_location is None:
        raise ValueError("Building must provide at least one identifying attribute")
    return building


def _map_units(commands: tuple[AddressUnitPayloadCommand, ...]) -> tuple[AddressContextUnitDraft, ...]:
    return tuple(
        AddressContextUnitDraft(
            unit_type=AddressUnitType(command.unit_type),
            value=require_non_blank_text(
                owner="AddressUnit",
                field_name="value",
                value=command.value,
            ),
            reference=_build_unit_reference(command.unit_type, command.value),
        )
        for command in commands
    )


def _map_unit_hierarchy(
    commands: tuple[AddressUnitHierarchyPayloadCommand, ...],
) -> tuple[AddressContextUnitHierarchyDraft, ...]:
    return tuple(
        AddressContextUnitHierarchyDraft(
            parent_ref=require_non_blank_text(
                owner="AddressUnitHierarchy",
                field_name="parent_ref",
                value=command.parent_ref,
            ),
            child_ref=require_non_blank_text(
                owner="AddressUnitHierarchy",
                field_name="child_ref",
                value=command.child_ref,
            ),
        )
        for command in commands
    )


def _map_assignments(
    commands: tuple[AddressAssignmentPayloadCommand, ...],
) -> tuple[AddressContextAssignmentDraft, ...]:
    return tuple(
        AddressContextAssignmentDraft(
            related_entity=RelatedEntityRef(
                entity_type=RelatedEntityType(command.related_entity.entity_type),
                entity_id=NodeId(command.related_entity.entity_id),
            ),
            relation_type=AddressRelationType(command.relation_type),
            valid_from=_parse_optional_datetime(command.valid_from, field_name="valid_from"),
            valid_to=_parse_optional_datetime(command.valid_to, field_name="valid_to"),
            source=require_optional_non_blank_text(
                owner="AddressAssignment",
                field_name="source",
                value=command.source,
            ),
            note=require_optional_non_blank_text(
                owner="AddressAssignment",
                field_name="note",
                value=command.note,
            ),
        )
        for command in commands
    )


def _parse_optional_datetime(value: str | None, *, field_name: str) -> datetime | None:
    if value is None:
        return None

    normalized_value = require_non_blank_text(
        owner="AddressAssignment",
        field_name=field_name,
        value=value,
    )
    try:
        return datetime.fromisoformat(normalized_value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"AddressAssignment {field_name} must be a valid ISO-8601 datetime") from error


def _validate_unit_hierarchy(address_context: AddressContextDraft) -> None:
    unit_references = tuple(unit.reference for unit in address_context.units)
    _validate_unique_unit_references(unit_references)
    _validate_hierarchy_edges(address_context.unit_hierarchy, unit_references)
    _validate_assignment_temporal_windows(address_context.assignments)


def _validate_unique_unit_references(unit_references: tuple[str, ...]) -> None:
    duplicate_references = tuple(
        reference
        for index, reference in enumerate(unit_references)
        if reference in unit_references[:index]
    )
    if duplicate_references:
        raise ValueError(
            "Address units must be unique within one address context: "
            + ", ".join(duplicate_references)
        )


def _validate_hierarchy_edges(
    hierarchy_edges: tuple[AddressContextUnitHierarchyDraft, ...],
    unit_references: tuple[str, ...],
) -> None:
    known_references = frozenset(unit_references)
    duplicate_edges: set[tuple[str, str]] = set()
    seen_edges: set[tuple[str, str]] = set()

    for edge in hierarchy_edges:
        if edge.parent_ref not in known_references:
            raise ValueError(f"Unit hierarchy parent_ref '{edge.parent_ref}' does not reference a declared unit")
        if edge.child_ref not in known_references:
            raise ValueError(f"Unit hierarchy child_ref '{edge.child_ref}' does not reference a declared unit")
        if edge.parent_ref == edge.child_ref:
            raise ValueError("Unit hierarchy must not contain self-references")

        edge_key = (edge.parent_ref, edge.child_ref)
        if edge_key in seen_edges:
            duplicate_edges.add(edge_key)
        seen_edges.add(edge_key)

    if duplicate_edges:
        raise ValueError(
            "Unit hierarchy edges must be unique: "
            + ", ".join(f"{parent}->{child}" for parent, child in sorted(duplicate_edges))
        )


def _validate_assignment_temporal_windows(
    assignments: tuple[AddressContextAssignmentDraft, ...],
) -> None:
    for assignment in assignments:
        if assignment.valid_from is None or assignment.valid_to is None:
            continue
        try:
            is_invalid_window = assignment.valid_to < assignment.valid_from
        except TypeError as error:
            raise ValueError(
                "AddressAssignment valid_from and valid_to must use comparable datetime values"
            ) from error
        if is_invalid_window:
            raise ValueError("AddressAssignment valid_to must not be earlier than valid_from")


def _build_unit_reference(unit_type: str, value: str) -> str:
    return f"{unit_type}:{require_non_blank_text(owner='AddressUnit', field_name='value', value=value)}"
