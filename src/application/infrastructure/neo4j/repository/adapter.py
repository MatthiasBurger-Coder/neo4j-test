"""Composable repository adapter bases for structured Neo4j access."""

from typing import Generic, TypeVar

from src.application.infrastructure.neo4j.repository.contracts import (
    CypherStatementBuilder,
    Neo4jResultProjector,
)
from src.application.infrastructure.neo4j.repository.executor import Neo4jRepositoryExecutor
from src.application.port.outbound.repository.read_repository import ReadRepositoryPort
from src.application.port.outbound.repository.write_repository import WriteRepositoryPort


TRequest = TypeVar("TRequest")
TResult = TypeVar("TResult")


class Neo4jReadRepositoryAdapter(ReadRepositoryPort[TRequest, TResult], Generic[TRequest, TResult]):
    """Base implementation for read-oriented Neo4j repository adapters."""

    def __init__(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement_builder: CypherStatementBuilder[TRequest],
        result_projector: Neo4jResultProjector[TResult],
        repository_executor: Neo4jRepositoryExecutor,
    ) -> None:
        self._repository_name = self._require_non_blank("repository_name", repository_name)
        self._operation_name = self._require_non_blank("operation_name", operation_name)
        self._statement_builder = statement_builder
        self._result_projector = result_projector
        self._repository_executor = repository_executor

    def execute(self, request_model: TRequest) -> TResult:
        """Build, execute, and project a read-side repository statement."""
        statement = self._statement_builder.build(request_model)
        return self._repository_executor.execute_read(
            repository_name=self._repository_name,
            operation_name=self._operation_name,
            statement=statement,
            result_projector=self._result_projector,
        )

    @staticmethod
    def _require_non_blank(field_name: str, value: str) -> str:
        normalized_value = value.strip()
        if normalized_value == "":
            raise ValueError(f"Neo4jReadRepositoryAdapter {field_name} must not be blank")
        return normalized_value


class Neo4jWriteRepositoryAdapter(WriteRepositoryPort[TRequest, TResult], Generic[TRequest, TResult]):
    """Base implementation for write-oriented Neo4j repository adapters."""

    def __init__(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement_builder: CypherStatementBuilder[TRequest],
        result_projector: Neo4jResultProjector[TResult],
        repository_executor: Neo4jRepositoryExecutor,
    ) -> None:
        self._repository_name = self._require_non_blank("repository_name", repository_name)
        self._operation_name = self._require_non_blank("operation_name", operation_name)
        self._statement_builder = statement_builder
        self._result_projector = result_projector
        self._repository_executor = repository_executor

    def execute(self, request_model: TRequest) -> TResult:
        """Build, execute, and project a write-side repository statement."""
        statement = self._statement_builder.build(request_model)
        return self._repository_executor.execute_write(
            repository_name=self._repository_name,
            operation_name=self._operation_name,
            statement=statement,
            result_projector=self._result_projector,
        )

    @staticmethod
    def _require_non_blank(field_name: str, value: str) -> str:
        normalized_value = value.strip()
        if normalized_value == "":
            raise ValueError(f"Neo4jWriteRepositoryAdapter {field_name} must not be blank")
        return normalized_value
