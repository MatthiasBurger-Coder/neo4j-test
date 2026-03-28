"""Unit tests for the base Neo4j repository adapters."""

from dataclasses import dataclass
import unittest
from typing import TypeVar

from src.adapters.outbound.persistence.neo4j.repository.adapter import (
    Neo4jReadRepositoryAdapter,
    Neo4jWriteRepositoryAdapter,
)
from src.adapters.outbound.persistence.neo4j.repository.contracts import (
    CypherStatementBuilder,
    Neo4jResultProjector,
)
from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement


TProjectedResult = TypeVar("TProjectedResult")


@dataclass(frozen=True, slots=True)
class _RequestModel:
    entity_id: str


class _RequestStatementBuilder(CypherStatementBuilder[_RequestModel]):
    def build(self, request_model: _RequestModel) -> CypherStatement:
        return CypherStatement(
            name="entity.by_id",
            cypher="MATCH (n {id: $entity_id}) RETURN n.id AS entity_id",
            parameters={"entity_id": request_model.entity_id},
        )


class _ListProjector(Neo4jResultProjector[list[dict[str, object]]]):
    def project(self, execution_result: Neo4jExecutionResult) -> list[dict[str, object]]:
        return [dict(row) for row in execution_result.records]


class _FakeRepositoryExecutor:
    def __init__(self) -> None:
        self.last_call = None

    def execute_read(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        self.last_call = (
            "read",
            {
                "repository_name": repository_name,
                "operation_name": operation_name,
                "statement": statement,
                "result_projector": result_projector,
            },
        )
        return result_projector.project(
            Neo4jExecutionResult(
                statement_name=statement.name,
                records=({"entity_id": statement.parameters["entity_id"]},),
                keys=("entity_id",),
                counters=Neo4jQueryCounters(),
            )
        )

    def execute_write(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TProjectedResult],
    ) -> TProjectedResult:
        self.last_call = (
            "write",
            {
                "repository_name": repository_name,
                "operation_name": operation_name,
                "statement": statement,
                "result_projector": result_projector,
            },
        )
        return result_projector.project(
            Neo4jExecutionResult(
                statement_name=statement.name,
                records=({"entity_id": statement.parameters["entity_id"]},),
                keys=("entity_id",),
                counters=Neo4jQueryCounters(contains_updates=True),
            )
        )


class Neo4jRepositoryAdapterTest(unittest.TestCase):
    def test_read_adapter_builds_statement_and_delegates_to_executor(self) -> None:
        executor = _FakeRepositoryExecutor()
        repository = Neo4jReadRepositoryAdapter[
            _RequestModel,
            list[dict[str, object]],
        ](
            repository_name="EntityReadRepository",
            operation_name="execute",
            statement_builder=_RequestStatementBuilder(),
            result_projector=_ListProjector(),
            repository_executor=executor,
        )

        result = repository.execute(_RequestModel(entity_id="n-1"))

        self.assertEqual([{"entity_id": "n-1"}], result)
        self.assertEqual("read", executor.last_call[0])
        self.assertEqual("entity.by_id", executor.last_call[1]["statement"].name)

    def test_write_adapter_builds_statement_and_delegates_to_executor(self) -> None:
        executor = _FakeRepositoryExecutor()
        repository = Neo4jWriteRepositoryAdapter[
            _RequestModel,
            list[dict[str, object]],
        ](
            repository_name="EntityWriteRepository",
            operation_name="execute",
            statement_builder=_RequestStatementBuilder(),
            result_projector=_ListProjector(),
            repository_executor=executor,
        )

        result = repository.execute(_RequestModel(entity_id="n-2"))

        self.assertEqual([{"entity_id": "n-2"}], result)
        self.assertEqual("write", executor.last_call[0])
        self.assertEqual("n-2", executor.last_call[1]["statement"].parameters["entity_id"])


if __name__ == "__main__":
    unittest.main()



