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
from src.application.addresses.address_write_port import AddressWriteError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
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
    def test_create_address_returns_mapped_address(self) -> None:
        executor = _PreparedWriteExecutor(
            execution_result=Neo4jExecutionResult(
                statement_name="address.create",
                records=(
                    {
                        "address_id": "addr-1",
                        "house_number": "42A",
                        "latitude": 52.52,
                        "longitude": 13.405,
                    },
                ),
                keys=("address_id", "house_number", "latitude", "longitude"),
                counters=Neo4jQueryCounters(contains_updates=True, nodes_created=1),
            )
        )
        adapter = Neo4jAddressWriteAdapter(executor)

        result = adapter.create_address(
            Address(
                id=NodeId("addr-1"),
                house_number="42A",
                geo_location=GeoLocation(latitude=52.52, longitude=13.405),
            )
        )

        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("create_address", executor.last_call["operation_name"])
        self.assertEqual("addr-1", executor.last_call["statement"].parameters["address_id"])
        self.assertEqual(52.52, executor.last_call["statement"].parameters["latitude"])

    def test_create_address_translates_technical_errors_to_port_error(self) -> None:
        adapter = Neo4jAddressWriteAdapter(
            _PreparedWriteExecutor(error=_create_write_error("OSError: database unavailable"))
        )

        with self.assertRaises(AddressWriteError) as raised_error:
            adapter.create_address(Address(id=NodeId("addr-1"), house_number="42A"))

        self.assertEqual("Address persistence failed", str(raised_error.exception))


def _create_write_error(technical_message: str) -> Neo4jWriteRepositoryError:
    return Neo4jWriteRepositoryError(
        message="Neo4j write repository operation failed",
        context=Neo4jRepositoryOperationContext(
            repository_name="Neo4jAddressWriteAdapter",
            operation_name="create_address",
            access_mode=Neo4jAccessMode.WRITE,
            statement_name="address.create",
            database_name="neo4j",
            correlation_id="corr-test",
        ),
        failure_stage="execution",
        technical_message=technical_message,
    )


if __name__ == "__main__":
    unittest.main()
