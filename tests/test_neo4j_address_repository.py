"""Unit tests for the concrete Neo4j address repository wiring."""

import unittest
from typing import TypeVar

from src.application.domain.addresses.model.address import Address
from src.application.domain.addresses.port.address_by_id_repository import FindAddressByIdQuery
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.infrastructure.neo4j.addresses.address_by_id_repository import Neo4jAddressByIdRepository
from src.application.infrastructure.neo4j.repository.contracts import Neo4jResultProjector
from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.application.infrastructure.neo4j.repository.statement import CypherStatement


TProjectedResult = TypeVar("TProjectedResult")


class _PreparedReadExecutor:
    def __init__(self, execution_result: Neo4jExecutionResult) -> None:
        self._execution_result = execution_result

    def execute_read(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        del repository_name, operation_name, statement
        return result_projector.project(self._execution_result)

    def execute_write(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        del repository_name, operation_name, statement, result_projector
        raise AssertionError("Write execution is not expected in address read repository tests")


class Neo4jAddressByIdRepositoryTest(unittest.TestCase):
    def test_repository_maps_address_domain_model(self) -> None:
        repository = Neo4jAddressByIdRepository(
            _PreparedReadExecutor(
                Neo4jExecutionResult(
                    statement_name="address.find_by_id",
                    records=(
                        {
                            "address_id": "addr-1",
                            "house_number": "42A",
                            "latitude": 52.52,
                            "longitude": 13.405,
                        },
                    ),
                    keys=("address_id", "house_number", "latitude", "longitude"),
                    counters=Neo4jQueryCounters(),
                )
            )
        )

        result = repository.execute(FindAddressByIdQuery(address_id=NodeId("addr-1")))

        self.assertIsInstance(result, Address)
        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("42A", result.house_number)
        self.assertTrue(result.has_geo_location())

    def test_repository_returns_none_when_no_address_exists(self) -> None:
        repository = Neo4jAddressByIdRepository(
            _PreparedReadExecutor(
                Neo4jExecutionResult(
                    statement_name="address.find_by_id",
                    records=(),
                    keys=(),
                    counters=Neo4jQueryCounters(),
                )
            )
        )

        result = repository.execute(FindAddressByIdQuery(address_id=NodeId("missing-address")))

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
