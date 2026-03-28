"""Transaction execution strategies for Neo4j read and write operations."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping
from typing import Generic, TypeVar

from src.adapters.outbound.persistence.neo4j.repository.access_mode import Neo4jAccessMode
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jTransactionProtocol, Neo4jTransactionSessionProtocol


TResult = TypeVar("TResult")


class Neo4jTransactionExecutionStrategy(ABC, Generic[TResult]):
    """Executes transactional work with a dedicated Neo4j session strategy."""

    access_mode: Neo4jAccessMode

    @abstractmethod
    def execute(
        self,
        session: Neo4jTransactionSessionProtocol,
        work: Callable[[Neo4jTransactionProtocol], TResult],
    ) -> TResult:
        """Execute transactional work inside a session."""


class Neo4jReadTransactionExecutionStrategy(Neo4jTransactionExecutionStrategy[TResult]):
    """Executes repository work using Neo4j read transactions."""

    access_mode = Neo4jAccessMode.READ

    def execute(
        self,
        session: Neo4jTransactionSessionProtocol,
        work: Callable[[Neo4jTransactionProtocol], TResult],
    ) -> TResult:
        return session.execute_read(work)


class Neo4jWriteTransactionExecutionStrategy(Neo4jTransactionExecutionStrategy[TResult]):
    """Executes repository work using Neo4j write transactions."""

    access_mode = Neo4jAccessMode.WRITE

    def execute(
        self,
        session: Neo4jTransactionSessionProtocol,
        work: Callable[[Neo4jTransactionProtocol], TResult],
    ) -> TResult:
        return session.execute_write(work)


def default_transaction_strategies() -> Mapping[Neo4jAccessMode, Neo4jTransactionExecutionStrategy[object]]:
    """Return the default transaction strategies keyed by access mode."""
    return {
        Neo4jAccessMode.READ: Neo4jReadTransactionExecutionStrategy(),
        Neo4jAccessMode.WRITE: Neo4jWriteTransactionExecutionStrategy(),
    }



