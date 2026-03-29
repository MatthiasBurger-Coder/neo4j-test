"""Unit tests for the Neo4j address write adapter."""

import unittest
from typing import TypeVar

from src.adapters.outbound.persistence.neo4j.addresses.address_write_adapter import (
    Neo4jAddressWriteAdapter,
)
from src.adapters.outbound.persistence.neo4j.repository.access_mode import Neo4jAccessMode
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.error import Neo4jWriteRepositoryError
from src.adapters.outbound.persistence.neo4j.repository.operation import Neo4jRepositoryOperationContext
from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement
from src.application.addresses.address_context import (
    AddressContextAddressDraft,
    AddressContextAssignmentDraft,
    AddressContextBuildingDraft,
    AddressContextCityDraft,
    AddressContextDraft,
    AddressContextStreetDraft,
    AddressContextUnitDraft,
    AddressContextUnitHierarchyDraft,
)
from src.application.addresses.address_write_port import AddressWriteError
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef, RelatedEntityType
from src.domain.shared.graph.model.node_id import NodeId


TProjectedResult = TypeVar("TProjectedResult")


class _PreparedWriteExecutor:
    def __init__(
        self,
        *,
        execution_result: Neo4jExecutionResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self._execution_result = execution_result
        self._error = error
        self.last_call: dict[str, object] | None = None

    def execute_read(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        del repository_name, operation_name, statement, result_projector
        raise AssertionError("Read execution is not expected in address write adapter tests")

    def execute_write(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        self.last_call = {
            "repository_name": repository_name,
            "operation_name": operation_name,
            "statement": statement,
        }
        if self._error is not None:
            raise self._error
        if self._execution_result is None:
            raise AssertionError("An execution result must be configured for write adapter tests")
        return result_projector.project(self._execution_result)


class Neo4jAddressWriteAdapterTest(unittest.TestCase):
    def test_create_address_returns_mapped_context_and_relationships(self) -> None:
        executor = _PreparedWriteExecutor(execution_result=_create_execution_result())
        adapter = Neo4jAddressWriteAdapter(executor)

        result = adapter.create_address(_create_address_context())

        self.assertEqual("addr-1", result.address.id.value)
        self.assertEqual("Marienplatz", result.street.name)
        self.assertEqual("Munich", result.city.name)
        self.assertEqual("Town Hall", result.building.name)
        self.assertEqual(("ENTRANCE", "FLOOR"), tuple(unit.unit_type.value for unit in result.units))
        self.assertEqual("person-123", result.assignments[0].related_entity.entity_id.value)
        self.assertEqual("create_address", executor.last_call["operation_name"])
        self.assertIn("MERGE (address:Address", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (street)-[street_in_city:STREET_IN_CITY", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (address)-[address_on_street:ADDRESS_ON_STREET", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (address)-[address_in_building:ADDRESS_IN_BUILDING", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (address)-[address_has_unit:ADDRESS_HAS_UNIT", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (parent_unit)-[unit_within_unit:ADDRESS_UNIT_WITHIN_UNIT", executor.last_call["statement"].cypher)
        self.assertIn("MERGE (related_entity)-[assignment:ADDRESS_ASSIGNMENT", executor.last_call["statement"].cypher)
        self.assertEqual("Marienplatz", executor.last_call["statement"].parameters["street"]["name"])
        self.assertEqual("Germany", executor.last_call["statement"].parameters["city"]["country"])
        self.assertEqual("Town Hall", executor.last_call["statement"].parameters["building"]["name"])
        self.assertEqual(2, len(executor.last_call["statement"].parameters["units"]))
        self.assertEqual(1, len(executor.last_call["statement"].parameters["unit_hierarchy"]))
        self.assertEqual(1, len(executor.last_call["statement"].parameters["assignments"]))

    def test_create_address_translates_technical_errors_to_port_error(self) -> None:
        adapter = Neo4jAddressWriteAdapter(
            _PreparedWriteExecutor(error=_create_write_error("OSError: database unavailable"))
        )

        with self.assertRaises(AddressWriteError) as raised_error:
            adapter.create_address(_create_address_context())

        self.assertEqual("Address context persistence failed", str(raised_error.exception))


def _create_address_context() -> AddressContextDraft:
    return AddressContextDraft(
        address=AddressContextAddressDraft(
            house_number="12A",
            geo_location=GeoLocation(latitude=48.137154, longitude=11.576124),
        ),
        street=AddressContextStreetDraft(name="Marienplatz"),
        city=AddressContextCityDraft(name="Munich", country="Germany", postal_code="80331"),
        building=AddressContextBuildingDraft(
            name="Town Hall",
            geo_location=GeoLocation(latitude=48.1372, longitude=11.5759),
        ),
        units=(
            AddressContextUnitDraft(
                unit_type=AddressUnitType.ENTRANCE,
                value="North",
                reference="ENTRANCE:North",
            ),
            AddressContextUnitDraft(
                unit_type=AddressUnitType.FLOOR,
                value="3",
                reference="FLOOR:3",
            ),
        ),
        unit_hierarchy=(
            AddressContextUnitHierarchyDraft(
                parent_ref="ENTRANCE:North",
                child_ref="FLOOR:3",
            ),
        ),
        assignments=(
            AddressContextAssignmentDraft(
                related_entity=RelatedEntityRef(
                    entity_type=RelatedEntityType.PERSON,
                    entity_id=NodeId("person-123"),
                ),
                relation_type=AddressRelationType.RESIDENCE,
                valid_from=None,
                valid_to=None,
                source="registry",
                note="Primary residence",
            ),
        ),
    )


def _create_execution_result() -> Neo4jExecutionResult:
    return Neo4jExecutionResult(
        statement_name="address_context.create",
        records=(
            {
                "address_id": "addr-1",
                "address_house_number": "12A",
                "address_latitude": 48.137154,
                "address_longitude": 11.576124,
                "street_id": "street-1",
                "street_name": "Marienplatz",
                "city_id": "city-1",
                "city_name": "Munich",
                "city_country": "Germany",
                "city_postal_code": "80331",
                "address_on_street_id": "rel-address-street-1",
                "street_in_city_id": "rel-street-city-1",
                "building_id": "building-1",
                "building_name": "Town Hall",
                "building_latitude": 48.1372,
                "building_longitude": 11.5759,
                "address_in_building_id": "rel-address-building-1",
                "units": [
                    {
                        "unit_id": "unit-1",
                        "unit_type": "ENTRANCE",
                        "value": "North",
                        "reference": "ENTRANCE:North",
                        "address_has_unit_id": "rel-address-unit-1",
                    },
                    {
                        "unit_id": "unit-2",
                        "unit_type": "FLOOR",
                        "value": "3",
                        "reference": "FLOOR:3",
                        "address_has_unit_id": "rel-address-unit-2",
                    },
                ],
                "unit_hierarchy": [
                    {
                        "relationship_id": "rel-unit-hierarchy-1",
                        "parent_unit_id": "unit-1",
                        "child_unit_id": "unit-2",
                    },
                ],
                "assignments": [
                    {
                        "assignment_id": "rel-assignment-1",
                        "related_entity_type": "PERSON",
                        "related_entity_id": "person-123",
                        "relation_type": "RESIDENCE",
                        "valid_from": "2024-01-01T00:00:00Z",
                        "valid_to": None,
                        "source": "registry",
                        "note": "Primary residence",
                    },
                ],
            },
        ),
        keys=(
            "address_id",
            "address_house_number",
            "address_latitude",
            "address_longitude",
            "street_id",
            "street_name",
            "city_id",
            "city_name",
            "city_country",
            "city_postal_code",
            "address_on_street_id",
            "street_in_city_id",
            "building_id",
            "building_name",
            "building_latitude",
            "building_longitude",
            "address_in_building_id",
            "units",
            "unit_hierarchy",
            "assignments",
        ),
        counters=Neo4jQueryCounters(contains_updates=True, nodes_created=5, relationships_created=6),
    )


def _create_write_error(technical_message: str) -> Neo4jWriteRepositoryError:
    return Neo4jWriteRepositoryError(
        message="Neo4j write repository operation failed",
        context=Neo4jRepositoryOperationContext(
            repository_name="Neo4jAddressWriteAdapter",
            operation_name="create_address",
            access_mode=Neo4jAccessMode.WRITE,
            statement_name="address_context.create",
            database_name="neo4j",
            correlation_id="corr-test",
        ),
        failure_stage="execution",
        technical_message=technical_message,
    )


if __name__ == "__main__":
    unittest.main()
