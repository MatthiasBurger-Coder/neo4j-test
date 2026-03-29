"""Cypher query definitions for address-context write operations."""

from src.adapters.outbound.persistence.neo4j.addresses.write_model import (
    CreateAddressContextWriteModel,
)
from src.adapters.outbound.persistence.neo4j.repository.contracts import CypherStatementBuilder
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement


class CreateAddressContextStatementBuilder(CypherStatementBuilder[CreateAddressContextWriteModel]):
    """Builds the create-side address-context statement from the write model."""

    def build(self, request_model: CreateAddressContextWriteModel) -> CypherStatement:
        return CypherStatement(
            name="address_context.create",
            cypher=_ADDRESS_CONTEXT_CREATE_QUERY.strip(),
            parameters={
                "address": {
                    "merge_key": request_model.address.merge_key,
                    "house_number": request_model.address.house_number,
                    "latitude": request_model.address.latitude,
                    "longitude": request_model.address.longitude,
                },
                "street": {
                    "merge_key": request_model.street.merge_key,
                    "name": request_model.street.name,
                },
                "city": {
                    "merge_key": request_model.city.merge_key,
                    "name": request_model.city.name,
                    "country": request_model.city.country,
                    "postal_code": request_model.city.postal_code,
                },
                "address_on_street_merge_key": request_model.address_on_street_merge_key,
                "street_in_city_merge_key": request_model.street_in_city_merge_key,
                "building": None
                if request_model.building is None
                else {
                    "merge_key": request_model.building.merge_key,
                    "relationship_merge_key": request_model.building.relationship_merge_key,
                    "name": request_model.building.name,
                    "latitude": request_model.building.latitude,
                    "longitude": request_model.building.longitude,
                },
                "units": [
                    {
                        "sort_index": unit.sort_index,
                        "merge_key": unit.merge_key,
                        "relationship_merge_key": unit.relationship_merge_key,
                        "reference": unit.reference,
                        "unit_type": unit.unit_type,
                        "value": unit.value,
                    }
                    for unit in request_model.units
                ],
                "unit_hierarchy": [
                    {
                        "sort_index": edge.sort_index,
                        "merge_key": edge.merge_key,
                        "parent_unit_merge_key": edge.parent_unit_merge_key,
                        "child_unit_merge_key": edge.child_unit_merge_key,
                    }
                    for edge in request_model.unit_hierarchy
                ],
                "assignments": [
                    {
                        "sort_index": assignment.sort_index,
                        "merge_key": assignment.merge_key,
                        "related_entity_merge_key": assignment.related_entity_merge_key,
                        "related_entity_type": assignment.related_entity_type,
                        "related_entity_id": assignment.related_entity_id,
                        "relation_type": assignment.relation_type,
                        "valid_from": assignment.valid_from,
                        "valid_to": assignment.valid_to,
                        "source": assignment.source,
                        "note": assignment.note,
                    }
                    for assignment in request_model.assignments
                ],
            },
        )


_ADDRESS_CONTEXT_CREATE_QUERY = """
MERGE (city:City {merge_key: $city.merge_key})
  ON CREATE SET city.id = randomUUID()
SET city.name = $city.name,
    city.country = $city.country,
    city.postal_code = $city.postal_code

MERGE (street:Street {merge_key: $street.merge_key})
  ON CREATE SET street.id = randomUUID()
SET street.name = $street.name

MERGE (street)-[street_in_city:STREET_IN_CITY {merge_key: $street_in_city_merge_key}]->(city)
  ON CREATE SET street_in_city.id = randomUUID()

MERGE (address:Address {merge_key: $address.merge_key})
  ON CREATE SET address.id = randomUUID()
SET address.house_number = $address.house_number,
    address.latitude = $address.latitude,
    address.longitude = $address.longitude

MERGE (address)-[address_on_street:ADDRESS_ON_STREET {merge_key: $address_on_street_merge_key}]->(street)
  ON CREATE SET address_on_street.id = randomUUID()

CALL {
  WITH address, $building AS building_data
  WITH address, building_data
  WHERE building_data IS NOT NULL
  MERGE (building:Building {merge_key: building_data.merge_key})
    ON CREATE SET building.id = randomUUID()
  SET building.name = building_data.name,
      building.latitude = building_data.latitude,
      building.longitude = building_data.longitude
  MERGE (address)-[address_in_building:ADDRESS_IN_BUILDING {merge_key: building_data.relationship_merge_key}]->(building)
    ON CREATE SET address_in_building.id = randomUUID()
  RETURN
    building.id AS building_id,
    building.name AS building_name,
    building.latitude AS building_latitude,
    building.longitude AS building_longitude,
    address_in_building.id AS address_in_building_id
  UNION
  WITH address, building_data
  WHERE building_data IS NULL
  RETURN
    NULL AS building_id,
    NULL AS building_name,
    NULL AS building_latitude,
    NULL AS building_longitude,
    NULL AS address_in_building_id
}

CALL {
  WITH address, $units AS unit_rows
  UNWIND unit_rows AS unit_row
  MERGE (unit:AddressUnit {merge_key: unit_row.merge_key})
    ON CREATE SET unit.id = randomUUID()
  SET unit.unit_type = unit_row.unit_type,
      unit.value = unit_row.value
  MERGE (address)-[address_has_unit:ADDRESS_HAS_UNIT {merge_key: unit_row.relationship_merge_key}]->(unit)
    ON CREATE SET address_has_unit.id = randomUUID()
  WITH unit_row, unit, address_has_unit
  ORDER BY unit_row.sort_index
  RETURN collect({
    unit_id: unit.id,
    unit_type: unit.unit_type,
    value: unit.value,
    reference: unit_row.reference,
    address_has_unit_id: address_has_unit.id
  }) AS units
}

CALL {
  WITH $unit_hierarchy AS hierarchy_rows
  UNWIND hierarchy_rows AS hierarchy_row
  MATCH (parent_unit:AddressUnit {merge_key: hierarchy_row.parent_unit_merge_key})
  MATCH (child_unit:AddressUnit {merge_key: hierarchy_row.child_unit_merge_key})
  MERGE (parent_unit)-[unit_within_unit:ADDRESS_UNIT_WITHIN_UNIT {merge_key: hierarchy_row.merge_key}]->(child_unit)
    ON CREATE SET unit_within_unit.id = randomUUID()
  WITH hierarchy_row, parent_unit, child_unit, unit_within_unit
  ORDER BY hierarchy_row.sort_index
  RETURN collect({
    relationship_id: unit_within_unit.id,
    parent_unit_id: parent_unit.id,
    child_unit_id: child_unit.id
  }) AS unit_hierarchy
}

CALL {
  WITH address, $assignments AS assignment_rows
  UNWIND assignment_rows AS assignment_row
  MERGE (related_entity:RelatedEntity {merge_key: assignment_row.related_entity_merge_key})
    ON CREATE SET related_entity.id = assignment_row.related_entity_id
  SET related_entity.entity_type = assignment_row.related_entity_type,
      related_entity.id = assignment_row.related_entity_id
  MERGE (related_entity)-[assignment:ADDRESS_ASSIGNMENT {merge_key: assignment_row.merge_key}]->(address)
    ON CREATE SET assignment.id = randomUUID()
  SET assignment.relation_type = assignment_row.relation_type,
      assignment.valid_from = assignment_row.valid_from,
      assignment.valid_to = assignment_row.valid_to,
      assignment.source = assignment_row.source,
      assignment.note = assignment_row.note
  WITH assignment_row, related_entity, assignment
  ORDER BY assignment_row.sort_index
  RETURN collect({
    assignment_id: assignment.id,
    related_entity_type: related_entity.entity_type,
    related_entity_id: related_entity.id,
    relation_type: assignment.relation_type,
    valid_from: assignment.valid_from,
    valid_to: assignment.valid_to,
    source: assignment.source,
    note: assignment.note
  }) AS assignments
}

RETURN
  address.id AS address_id,
  address.house_number AS address_house_number,
  address.latitude AS address_latitude,
  address.longitude AS address_longitude,
  street.id AS street_id,
  street.name AS street_name,
  city.id AS city_id,
  city.name AS city_name,
  city.country AS city_country,
  city.postal_code AS city_postal_code,
  address_on_street.id AS address_on_street_id,
  street_in_city.id AS street_in_city_id,
  building_id,
  building_name,
  building_latitude,
  building_longitude,
  address_in_building_id,
  units,
  unit_hierarchy,
  assignments
"""
