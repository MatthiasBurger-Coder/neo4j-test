"""Composable contracts for building statements, projecting results, and executing repository work."""

from abc import ABC, abstractmethod
from typing import Generic, Protocol, TypeVar, runtime_checkable

from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult
from src.application.infrastructure.neo4j.repository.statement import CypherStatement


TRequest = TypeVar("TRequest")
TResult = TypeVar("TResult")
TProjectedResult = TypeVar("TProjectedResult")


class CypherStatementBuilder(ABC, Generic[TRequest]):
    """Builds a structured Cypher statement from an application request model."""

    @abstractmethod
    def build(self, request_model: TRequest) -> CypherStatement:
        """Create a Cypher statement from an incoming repository request."""


class Neo4jResultProjector(ABC, Generic[TResult]):
    """Projects a plain execution result into the target repository return type."""

    @abstractmethod
    def project(self, execution_result: Neo4jExecutionResult) -> TResult:
        """Convert a plain Neo4j execution result into the adapter output model."""


@runtime_checkable
class Neo4jRepositoryExecutorProtocol(Protocol):
    """Structural contract for repository executors used by the adapter base classes."""

    def execute_read(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: "Neo4jResultProjector[TProjectedResult]",
    ) -> TProjectedResult:
        """Execute and project a read-side repository statement."""

    def execute_write(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: "Neo4jResultProjector[TProjectedResult]",
    ) -> TProjectedResult:
        """Execute and project a write-side repository statement."""
