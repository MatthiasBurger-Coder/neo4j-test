"""Composable contracts for building statements, projecting results, and executing repository work."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator, Mapping
from typing import Any, Generic, Protocol, TypeVar, runtime_checkable

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
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


@runtime_checkable
class Neo4jQueryFactoryProtocol(Protocol):
    """Creates driver-native query objects without leaking driver imports into the executor base."""

    def create(self, *, cypher: str, metadata: Mapping[str, object]) -> object:
        """Build a query object understood by the active Neo4j driver adapter."""


@runtime_checkable
class Neo4jExecutionFailureClassifierProtocol(Protocol):
    """Identifies technical execution failures that should be translated for repository callers."""

    def is_execution_failure(self, error: BaseException) -> bool:
        """Return whether the given error belongs to the driver/infrastructure execution boundary."""


@runtime_checkable
class Neo4jResultRecordProtocol(Protocol):
    """Minimal record protocol needed to materialize driver results."""

    def data(self) -> Mapping[str, Any]:
        """Return a plain mapping representation of the current result row."""


@runtime_checkable
class Neo4jResultCountersProtocol(Protocol):
    """Minimal summary counter contract needed for driver-agnostic result extraction."""

    nodes_created: int
    nodes_deleted: int
    relationships_created: int
    relationships_deleted: int
    properties_set: int
    labels_added: int
    labels_removed: int
    indexes_added: int
    indexes_removed: int
    constraints_added: int
    constraints_removed: int
    contains_updates: bool
    contains_system_updates: bool


@runtime_checkable
class Neo4jResultSummaryProtocol(Protocol):
    """Minimal query summary contract needed by the repository executor."""

    counters: Neo4jResultCountersProtocol
    query_type: str | None
    database: str | None


@runtime_checkable
class Neo4jResultCursorProtocol(Protocol):
    """Minimal cursor contract needed to materialize execution results."""

    def keys(self) -> Iterable[str]:
        """Return the projected column names for the query result."""

    def __iter__(self) -> Iterator[Neo4jResultRecordProtocol]:
        """Yield result records."""

    def consume(self) -> Neo4jResultSummaryProtocol:
        """Consume the cursor and return the execution summary."""


@runtime_checkable
class Neo4jTransactionProtocol(Protocol):
    """Minimal transaction contract needed by the repository executor."""

    def run(self, query: object, parameters: Mapping[str, Any]) -> Neo4jResultCursorProtocol:
        """Run a prepared statement with parameters inside the current transaction."""


@runtime_checkable
class Neo4jTransactionSessionProtocol(Protocol):
    """Opaque context-managed session used by transaction execution strategies."""

    def __enter__(self) -> "Neo4jTransactionSessionProtocol":
        """Enter the underlying session context."""

    def __exit__(self, exc_type: object, exc: object, tb: object) -> object:
        """Leave the underlying session context."""

    def execute_read(self, work: Callable[[Neo4jTransactionProtocol], TProjectedResult]) -> TProjectedResult:
        """Execute work in a read transaction."""

    def execute_write(self, work: Callable[[Neo4jTransactionProtocol], TProjectedResult]) -> TProjectedResult:
        """Execute work in a write transaction."""


@runtime_checkable
class Neo4jSessionProviderProtocol(Protocol):
    """Abstraction for opening access-mode-specific Neo4j sessions."""

    database: str

    def open_session(self, access_mode: Neo4jAccessMode) -> Neo4jTransactionSessionProtocol:
        """Open a session for the requested repository access mode."""
