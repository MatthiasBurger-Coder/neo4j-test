"""Result projectors for address-context write operations."""

from datetime import datetime
from typing import Mapping

from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.result import (
    CypherRow,
    Neo4jExecutionResult,
    require_row_value,
)
from src.application.addresses.address_context import CreatedAddressContext
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.address_assignment import AddressAssignment
from src.domain.addresses.model.address_has_unit import AddressHasUnit
from src.domain.addresses.model.address_in_building import AddressInBuilding
from src.domain.addresses.model.address_on_street import AddressOnStreet
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit import AddressUnit
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.address_unit_within_unit import AddressUnitWithinUnit
from src.domain.addresses.model.building import Building
from src.domain.addresses.model.city import City
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef, RelatedEntityType
from src.domain.addresses.model.street import Street
from src.domain.addresses.model.street_in_city import StreetInCity
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId


class CreatedAddressContextProjector(Neo4jResultProjector[CreatedAddressContext]):
    """Projects an execution result to the created address context."""

    def project(self, execution_result: Neo4jExecutionResult) -> CreatedAddressContext:
        return _CREATE_RESULT_HANDLERS.get(
            execution_result.record_count,
            _raise_invalid_create_result,
        )(execution_result)


def _map_created_address_context(execution_result: Neo4jExecutionResult) -> CreatedAddressContext:
    row = execution_result.records[0]
    address = _map_address(row)
    street = _map_street(row)
    city = _map_city(row)
    building = _map_building(row)
    units = _map_units(row)

    return CreatedAddressContext(
        address=address,
        street=street,
        city=city,
        address_on_street=AddressOnStreet(
            id=RelationshipId(_require_string_value(row, statement_name=execution_result.statement_name, field_name="address_on_street_id")),
            address_id=address.id,
            street_id=street.id,
        ),
        street_in_city=StreetInCity(
            id=RelationshipId(_require_string_value(row, statement_name=execution_result.statement_name, field_name="street_in_city_id")),
            street_id=street.id,
            city_id=city.id,
        ),
        building=building,
        address_in_building=_map_address_in_building(row, address_id=address.id, building_id=None if building is None else building.id),
        units=units,
        address_has_units=_map_address_has_units(row, address_id=address.id, units=units),
        unit_hierarchy=_map_unit_hierarchy(row),
        assignments=_map_assignments(row, address_id=address.id),
    )


def _map_address(row: CypherRow) -> Address:
    return Address(
        id=NodeId(_require_string_value(row, statement_name="address_context.create", field_name="address_id")),
        house_number=_require_string_value(row, statement_name="address_context.create", field_name="address_house_number"),
        geo_location=_map_geo_location(
            latitude=row.get("address_latitude"),
            longitude=row.get("address_longitude"),
        ),
    )


def _map_street(row: CypherRow) -> Street:
    return Street(
        id=NodeId(_require_string_value(row, statement_name="address_context.create", field_name="street_id")),
        name=_require_string_value(row, statement_name="address_context.create", field_name="street_name"),
    )


def _map_city(row: CypherRow) -> City:
    return City(
        id=NodeId(_require_string_value(row, statement_name="address_context.create", field_name="city_id")),
        name=_require_string_value(row, statement_name="address_context.create", field_name="city_name"),
        country=_require_string_value(row, statement_name="address_context.create", field_name="city_country"),
        postal_code=_optional_string(row.get("city_postal_code")),
    )


def _map_building(row: CypherRow) -> Building | None:
    building_id = row.get("building_id")
    if building_id is None:
        return None

    return Building(
        id=NodeId(str(building_id)),
        name=_optional_string(row.get("building_name")),
        geo_location=_map_geo_location(
            latitude=row.get("building_latitude"),
            longitude=row.get("building_longitude"),
        ),
    )


def _map_address_in_building(
    row: CypherRow,
    *,
    address_id: NodeId,
    building_id: NodeId | None,
) -> AddressInBuilding | None:
    relationship_id = row.get("address_in_building_id")
    if relationship_id is None or building_id is None:
        return None

    return AddressInBuilding(
        id=RelationshipId(str(relationship_id)),
        address_id=address_id,
        building_id=building_id,
    )


def _map_units(row: CypherRow) -> tuple[AddressUnit, ...]:
    unit_rows = _require_list(row, field_name="units")
    return tuple(
        AddressUnit(
            id=NodeId(_require_map_string_value(unit_row, field_name="unit_id")),
            unit_type=AddressUnitType(_require_map_string_value(unit_row, field_name="unit_type")),
            value=_require_map_string_value(unit_row, field_name="value"),
        )
        for unit_row in unit_rows
    )


def _map_address_has_units(
    row: CypherRow,
    *,
    address_id: NodeId,
    units: tuple[AddressUnit, ...],
) -> tuple[AddressHasUnit, ...]:
    unit_ids_by_index = tuple(unit.id for unit in units)
    unit_rows = _require_list(row, field_name="units")
    return tuple(
        AddressHasUnit(
            id=RelationshipId(_require_map_string_value(unit_row, field_name="address_has_unit_id")),
            address_id=address_id,
            address_unit_id=unit_ids_by_index[index],
        )
        for index, unit_row in enumerate(unit_rows)
    )


def _map_unit_hierarchy(row: CypherRow) -> tuple[AddressUnitWithinUnit, ...]:
    hierarchy_rows = _require_list(row, field_name="unit_hierarchy")
    return tuple(
        AddressUnitWithinUnit(
            id=RelationshipId(_require_map_string_value(hierarchy_row, field_name="relationship_id")),
            parent_unit_id=NodeId(_require_map_string_value(hierarchy_row, field_name="parent_unit_id")),
            child_unit_id=NodeId(_require_map_string_value(hierarchy_row, field_name="child_unit_id")),
        )
        for hierarchy_row in hierarchy_rows
    )


def _map_assignments(row: CypherRow, *, address_id: NodeId) -> tuple[AddressAssignment, ...]:
    assignment_rows = _require_list(row, field_name="assignments")
    return tuple(
        AddressAssignment(
            id=RelationshipId(_require_map_string_value(assignment_row, field_name="assignment_id")),
            related_entity=RelatedEntityRef(
                entity_type=RelatedEntityType(_require_map_string_value(assignment_row, field_name="related_entity_type")),
                entity_id=NodeId(_require_map_string_value(assignment_row, field_name="related_entity_id")),
            ),
            address_id=address_id,
            relation_type=AddressRelationType(_require_map_string_value(assignment_row, field_name="relation_type")),
            valid_from=_parse_optional_datetime(assignment_row.get("valid_from")),
            valid_to=_parse_optional_datetime(assignment_row.get("valid_to")),
            source=_optional_string(assignment_row.get("source")),
            note=_optional_string(assignment_row.get("note")),
        )
        for assignment_row in assignment_rows
    )


def _map_geo_location(*, latitude: object, longitude: object) -> GeoLocation | None:
    if latitude is None and longitude is None:
        return None
    if latitude is None or longitude is None:
        raise ValueError(
            f"Geo location must provide both latitude and longitude or neither (latitude={latitude!r}, longitude={longitude!r})"
        )
    return GeoLocation(latitude=float(latitude), longitude=float(longitude))


def _parse_optional_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def _require_string_value(
    row: CypherRow,
    *,
    statement_name: str,
    field_name: str,
) -> str:
    return str(require_row_value(statement_name=statement_name, row=row, field_name=field_name))


def _optional_string(value: object) -> str | None:
    return None if value is None else str(value)


def _require_list(row: CypherRow, *, field_name: str) -> list[Mapping[str, object]]:
    list_value = row.get(field_name, [])
    if not isinstance(list_value, list):
        raise ValueError(f"Field '{field_name}' must be returned as a list")
    return [_require_map(item, field_name=field_name) for item in list_value]


def _require_map(value: object, *, field_name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"Field '{field_name}' must contain only map values")
    return value


def _require_map_string_value(value: Mapping[str, object], *, field_name: str) -> str:
    try:
        field_value = value[field_name]
    except KeyError as error:
        raise ValueError(f"Returned map is missing required field '{field_name}'") from error
    return str(field_value)


def _raise_invalid_create_result(execution_result: Neo4jExecutionResult) -> CreatedAddressContext:
    raise ValueError(
        f"Statement '{execution_result.statement_name}' expected exactly one address-context record "
        f"but received {execution_result.record_count}"
    )


_CREATE_RESULT_HANDLERS = {
    1: _map_created_address_context,
}
