"""Composable repository adapter bases for structured Neo4j access."""

from abc import ABC
from typing import Generic, TypeVar

from src.application.infrastructure.neo4j.repository.contracts import (
    CypherStatementBuilder,
    Neo4jRepositoryExecutorProtocol,
    Neo4jResultProjector,
)
from src.application.infrastructure.neo4j.repository.statement import CypherStatement
from src.application.infrastructure.validation import require_non_blank
from src.application.port.outbound.repository.read_repository import ReadRepositoryPort
from src.application.port.outbound.repository.write_repository import WriteRepositoryPort


TRequest = TypeVar("TRequest")
TResult = TypeVar("TResult")


class Neo4jRepositoryAdapterBase(ABC, Generic[TRequest, TResult]):
    """Holds common validated wiring for concrete Neo4j repository adapters."""

    def __init__(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement_builder: CypherStatementBuilder[TRequest],
        result_projector: Neo4jResultProjector[TResult],
        repository_executor: Neo4jRepositoryExecutorProtocol,
    ) -> None:
        self._repository_name = require_non_blank(
            owner=self.__class__.__name__,
            field_name="repository_name",
            value=repository_name,
        )
        self._operation_name = require_non_blank(
            owner=self.__class__.__name__,
            field_name="operation_name",
            value=operation_name,
        )
        self._statement_builder = statement_builder
        self._result_projector = result_projector
        self._repository_executor = repository_executor

    def _build_statement(self, request_model: TRequest) -> CypherStatement:
        return self._statement_builder.build(request_model)


class Neo4jReadRepositoryAdapter(
    Neo4jRepositoryAdapterBase[TRequest, TResult],
    ReadRepositoryPort[TRequest, TResult],
    Generic[TRequest, TResult],
):
    """Base implementation for read-oriented Neo4j repository adapters."""

    def execute(self, request_model: TRequest) -> TResult:
        """Build, execute, and project a read-side repository statement."""
        statement = self._build_statement(request_model)
        return self._repository_executor.execute_read(
            repository_name=self._repository_name,
            operation_name=self._operation_name,
            statement=statement,
            result_projector=self._result_projector,
        )


class Neo4jWriteRepositoryAdapter(
    Neo4jRepositoryAdapterBase[TRequest, TResult],
    WriteRepositoryPort[TRequest, TResult],
    Generic[TRequest, TResult],
):
    """Base implementation for write-oriented Neo4j repository adapters."""

    def execute(self, request_model: TRequest) -> TResult:
        """Build, execute, and project a write-side repository statement."""
        statement = self._build_statement(request_model)
        return self._repository_executor.execute_write(
            repository_name=self._repository_name,
            operation_name=self._operation_name,
            statement=statement,
            result_projector=self._result_projector,
        )
