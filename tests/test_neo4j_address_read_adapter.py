"""Unit tests for the Neo4j address read adapter."""

import unittest
from typing import TypeVar

from src.adapters.outbound.persistence.neo4j.addresses.address_read_adapter import Neo4jAddressReadAdapter
from src.adapters.outbound.persistence.neo4j.repository.access_mode import Neo4jAccessMode
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jResultProjector
from src.adapters.outbound.persistence.neo4j.repository.error import Neo4jReadRepositoryError
from src.adapters.outbound.persistence.neo4j.repository.operation import Neo4jRepositoryOperationContext
from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement
from src.domain.addresses.model.address import Address
from src.domain.addresses.ports.address_read_repository import AddressReadCriteria
from src.domain.shared.graph.model.node_id import NodeId


TProjectedResult = TypeVar("TProjectedResult")


class _PreparedReadExecutor:
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
        self.last_call = {
            "repository_name": repository_name,
            "operation_name": operation_name,
            "statement": statement,
        }
        if self._error is not None:
            raise self._error
        if self._execution_result is None:
            raise AssertionError("An execution result must be configured for read adapter tests")
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
        raise AssertionError("Write execution is not expected in address read adapter tests")


class Neo4jAddressReadAdapterTest(unittest.TestCase):
    def test_find_by_id_returns_mapped_address(self) -> None:
        adapter = Neo4jAddressReadAdapter(
            _PreparedReadExecutor(
                execution_result=Neo4jExecutionResult(
                    statement_name="address.find_by_criteria",
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

        result = adapter.find_by_id(NodeId("addr-1"))

        self.assertIsInstance(result, Address)
        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("42A", result.house_number)
        self.assertTrue(result.has_geo_location())

    def test_find_by_id_returns_none_when_no_address_matches(self) -> None:
        adapter = Neo4jAddressReadAdapter(
            _PreparedReadExecutor(
                execution_result=Neo4jExecutionResult(
                    statement_name="address.find_by_criteria",
                    records=(),
                    keys=(),
                    counters=Neo4jQueryCounters(),
                )
            )
        )

        result = adapter.find_by_id(NodeId("missing-address"))

        self.assertIsNone(result)

    def test_find_all_returns_multiple_addresses(self) -> None:
        executor = _PreparedReadExecutor(
            execution_result=Neo4jExecutionResult(
                statement_name="address.find_by_criteria",
                records=(
                    {
                        "address_id": "addr-1",
                        "house_number": "42A",
                        "latitude": None,
                        "longitude": None,
                    },
                    {
                        "address_id": "addr-2",
                        "house_number": "43",
                        "latitude": 52.53,
                        "longitude": 13.41,
                    },
                ),
                keys=("address_id", "house_number", "latitude", "longitude"),
                counters=Neo4jQueryCounters(),
            )
        )
        adapter = Neo4jAddressReadAdapter(executor)

        result = adapter.find_all()

        self.assertEqual(("addr-1", "addr-2"), tuple(address.id.value for address in result))
        self.assertEqual(("42A", "43"), tuple(address.house_number for address in result))
        self.assertEqual("find_all", executor.last_call["operation_name"])

    def test_find_all_returns_empty_tuple_for_empty_resultset(self) -> None:
        adapter = Neo4jAddressReadAdapter(
            _PreparedReadExecutor(
                execution_result=Neo4jExecutionResult(
                    statement_name="address.find_by_criteria",
                    records=(),
                    keys=(),
                    counters=Neo4jQueryCounters(),
                )
            )
        )

        result = adapter.find_all()

        self.assertEqual((), result)

    def test_find_by_criteria_passes_filter_parameters_to_statement(self) -> None:
        executor = _PreparedReadExecutor(
            execution_result=Neo4jExecutionResult(
                statement_name="address.find_by_criteria",
                records=(),
                keys=(),
                counters=Neo4jQueryCounters(),
            )
        )
        adapter = Neo4jAddressReadAdapter(executor)

        adapter.find_by_criteria(
            AddressReadCriteria(address_ids=(NodeId("addr-1"), NodeId("addr-2")))
        )

        self.assertEqual("find_by_criteria", executor.last_call["operation_name"])
        self.assertEqual(
            ("addr-1", "addr-2"),
            executor.last_call["statement"].parameters["address_ids"],
        )
        self.assertIn(
            "WHERE address.id IN $address_ids",
            executor.last_call["statement"].cypher,
        )

    def test_find_by_id_propagates_translated_read_errors(self) -> None:
        adapter = Neo4jAddressReadAdapter(
            _PreparedReadExecutor(error=_create_read_error("OSError: database unavailable"))
        )

        with self.assertRaises(Neo4jReadRepositoryError) as raised_error:
            adapter.find_by_id(NodeId("addr-1"))

        self.assertIn("technical_error=OSError: database unavailable", str(raised_error.exception))


def _create_read_error(technical_message: str) -> Neo4jReadRepositoryError:
    return Neo4jReadRepositoryError(
        message="Neo4j read repository operation failed",
        context=Neo4jRepositoryOperationContext(
            repository_name="Neo4jAddressReadAdapter",
            operation_name="find_by_id",
            access_mode=Neo4jAccessMode.READ,
            statement_name="address.find_by_criteria",
            database_name="neo4j",
            correlation_id="corr-test",
        ),
        failure_stage="execution",
        technical_message=technical_message,
    )


if __name__ == "__main__":
    unittest.main()
