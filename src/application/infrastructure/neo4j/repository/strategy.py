"""Transaction execution strategies for Neo4j read and write operations."""

from abc import ABC, abstractmethod
from typing import Callable, Generic, Mapping, Protocol, TypeVar

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode


TResult = TypeVar("TResult")
TTransaction = TypeVar("TTransaction")


class Neo4jSessionProtocol(Protocol[TTransaction]):
    """Opaque session contract needed by transaction strategies."""

    def execute_read(self, work: Callable[[TTransaction], TResult]) -> TResult:
        """Execute work inside a read transaction."""

    def execute_write(self, work: Callable[[TTransaction], TResult]) -> TResult:
        """Execute work inside a write transaction."""


class Neo4jTransactionExecutionStrategy(ABC, Generic[TResult]):
    """Executes transactional work with a dedicated Neo4j session strategy."""

    access_mode: Neo4jAccessMode

    @abstractmethod
    def execute(self, session: Neo4jSessionProtocol[object], work: Callable[[object], TResult]) -> TResult:
        """Execute transactional work inside a session."""


class Neo4jReadTransactionExecutionStrategy(Neo4jTransactionExecutionStrategy[TResult]):
    """Executes repository work using Neo4j read transactions."""

    access_mode = Neo4jAccessMode.READ

    def execute(self, session: Neo4jSessionProtocol[object], work: Callable[[object], TResult]) -> TResult:
        return session.execute_read(work)


class Neo4jWriteTransactionExecutionStrategy(Neo4jTransactionExecutionStrategy[TResult]):
    """Executes repository work using Neo4j write transactions."""

    access_mode = Neo4jAccessMode.WRITE

    def execute(self, session: Neo4jSessionProtocol[object], work: Callable[[object], TResult]) -> TResult:
        return session.execute_write(work)


def default_transaction_strategies() -> Mapping[Neo4jAccessMode, Neo4jTransactionExecutionStrategy[object]]:
    """Return the default transaction strategies keyed by access mode."""
    return {
        Neo4jAccessMode.READ: Neo4jReadTransactionExecutionStrategy(),
        Neo4jAccessMode.WRITE: Neo4jWriteTransactionExecutionStrategy(),
    }
