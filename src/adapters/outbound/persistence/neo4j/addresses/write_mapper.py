"""Write-side mappers for Neo4j address-context persistence."""

from src.adapters.outbound.persistence.neo4j.addresses.write_model import (
    CreateAddressAssignmentWriteModel,
    CreateAddressContextWriteModel,
    CreateAddressNodeWriteModel,
    CreateAddressUnitHierarchyWriteModel,
    CreateAddressUnitWriteModel,
    CreateBuildingNodeWriteModel,
    CreateCityNodeWriteModel,
    CreateStreetNodeWriteModel,
)
from src.application.addresses.address_context import AddressContextDraft


class AddressContextToCreateAddressContextWriteModelMapper:
    """Maps the validated address-context draft to the Neo4j write model."""

    def map(self, address_context: AddressContextDraft) -> CreateAddressContextWriteModel:
        """Create the write model required by the address-context create statement."""
        city_merge_key = _build_city_merge_key(address_context)
        street_merge_key = _build_street_merge_key(address_context, city_merge_key=city_merge_key)
        address_merge_key = _build_address_merge_key(
            address_context,
            street_merge_key=street_merge_key,
            city_merge_key=city_merge_key,
        )

        unit_merge_keys_by_reference = {
            unit.reference: _build_unit_merge_key(address_merge_key=address_merge_key, reference=unit.reference)
            for unit in address_context.units
        }

        return CreateAddressContextWriteModel(
            address=CreateAddressNodeWriteModel(
                merge_key=address_merge_key,
                house_number=address_context.address.house_number,
                latitude=_latitude_of(address_context.address.geo_location),
                longitude=_longitude_of(address_context.address.geo_location),
            ),
            street=CreateStreetNodeWriteModel(
                merge_key=street_merge_key,
                name=address_context.street.name,
            ),
            city=CreateCityNodeWriteModel(
                merge_key=city_merge_key,
                name=address_context.city.name,
                country=address_context.city.country,
                postal_code=address_context.city.postal_code,
            ),
            address_on_street_merge_key=_normalize_key("address_on_street", address_merge_key, street_merge_key),
            street_in_city_merge_key=_normalize_key("street_in_city", street_merge_key, city_merge_key),
            building=_map_building(address_context, address_merge_key=address_merge_key),
            units=tuple(
                CreateAddressUnitWriteModel(
                    sort_index=index,
                    merge_key=unit_merge_keys_by_reference[unit.reference],
                    relationship_merge_key=_normalize_key(
                        "address_has_unit",
                        address_merge_key,
                        unit_merge_keys_by_reference[unit.reference],
                    ),
                    reference=unit.reference,
                    unit_type=unit.unit_type.value,
                    value=unit.value,
                )
                for index, unit in enumerate(address_context.units)
            ),
            unit_hierarchy=tuple(
                CreateAddressUnitHierarchyWriteModel(
                    sort_index=index,
                    merge_key=_normalize_key(
                        "address_unit_within_unit",
                        unit_merge_keys_by_reference[hierarchy.parent_ref],
                        unit_merge_keys_by_reference[hierarchy.child_ref],
                    ),
                    parent_unit_merge_key=unit_merge_keys_by_reference[hierarchy.parent_ref],
                    child_unit_merge_key=unit_merge_keys_by_reference[hierarchy.child_ref],
                )
                for index, hierarchy in enumerate(address_context.unit_hierarchy)
            ),
            assignments=tuple(
                CreateAddressAssignmentWriteModel(
                    sort_index=index,
                    merge_key=_normalize_key(
                        "address_assignment",
                        _normalize_key(
                            assignment.related_entity.entity_type.value,
                            assignment.related_entity.entity_id.value,
                        ),
                        address_merge_key,
                        assignment.relation_type.value,
                        _string_value_of(assignment.valid_from),
                        _string_value_of(assignment.valid_to),
                        assignment.source,
                        assignment.note,
                    ),
                    related_entity_merge_key=_normalize_key(
                        assignment.related_entity.entity_type.value,
                        assignment.related_entity.entity_id.value,
                    ),
                    related_entity_type=assignment.related_entity.entity_type.value,
                    related_entity_id=assignment.related_entity.entity_id.value,
                    relation_type=assignment.relation_type.value,
                    valid_from=_string_value_of(assignment.valid_from),
                    valid_to=_string_value_of(assignment.valid_to),
                    source=assignment.source,
                    note=assignment.note,
                )
                for index, assignment in enumerate(address_context.assignments)
            ),
        )


def _map_building(
    address_context: AddressContextDraft,
    *,
    address_merge_key: str,
) -> CreateBuildingNodeWriteModel | None:
    if address_context.building is None:
        return None

    building_merge_key = _normalize_key(
        "building",
        address_context.building.name,
        _latitude_of(address_context.building.geo_location),
        _longitude_of(address_context.building.geo_location),
    )
    return CreateBuildingNodeWriteModel(
        merge_key=building_merge_key,
        relationship_merge_key=_normalize_key("address_in_building", address_merge_key, building_merge_key),
        name=address_context.building.name,
        latitude=_latitude_of(address_context.building.geo_location),
        longitude=_longitude_of(address_context.building.geo_location),
    )


def _build_city_merge_key(address_context: AddressContextDraft) -> str:
    return _normalize_key(
        "city",
        address_context.city.name,
        address_context.city.country,
        address_context.city.postal_code,
    )


def _build_street_merge_key(address_context: AddressContextDraft, *, city_merge_key: str) -> str:
    return _normalize_key(
        "street",
        address_context.street.name,
        city_merge_key,
    )


def _build_address_merge_key(
    address_context: AddressContextDraft,
    *,
    street_merge_key: str,
    city_merge_key: str,
) -> str:
    return _normalize_key(
        "address",
        address_context.address.house_number,
        street_merge_key,
        city_merge_key,
        _latitude_of(address_context.address.geo_location),
        _longitude_of(address_context.address.geo_location),
    )


def _build_unit_merge_key(*, address_merge_key: str, reference: str) -> str:
    return _normalize_key("address_unit", address_merge_key, reference)


def _normalize_key(*parts: object | None) -> str:
    return "|".join(
        _normalize_key_part(part)
        for part in parts
    )


def _normalize_key_part(part: object | None) -> str:
    if part is None:
        return ""
    return str(part).strip().lower()


def _latitude_of(geo_location) -> float | None:
    return None if geo_location is None else geo_location.latitude


def _longitude_of(geo_location) -> float | None:
    return None if geo_location is None else geo_location.longitude


def _string_value_of(value) -> str | None:
    return None if value is None else value.isoformat().replace("+00:00", "Z")
