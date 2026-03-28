"""Driver-specific Neo4j integration points isolated from the reusable repository base."""

from collections.abc import Mapping

from src.adapters.outbound.persistence.neo4j.repository.contracts import (
    Neo4jExecutionFailureClassifierProtocol,
    Neo4jTransactionProtocol,
    Neo4jTransactionWorkFactoryProtocol,
)


class Neo4jManagedTransactionWorkFactory(Neo4jTransactionWorkFactoryProtocol):
    """Decorates managed transaction work with Neo4j driver metadata."""

    def create(
        self,
        *,
        metadata: Mapping[str, object],
        work,
    ):
        from neo4j import unit_of_work

        return unit_of_work(metadata=dict(metadata))(work)


class Neo4jDriverExecutionFailureClassifier(Neo4jExecutionFailureClassifierProtocol):
    """Classifies driver and transport failures without forcing driver imports during module import."""

    def is_execution_failure(self, error: BaseException) -> bool:
        return isinstance(error, (*self._driver_error_types(), OSError))

    @staticmethod
    def _driver_error_types() -> tuple[type[BaseException], ...]:
        try:
            from neo4j.exceptions import DriverError, Neo4jError
        except ModuleNotFoundError:
            return ()

        return (Neo4jError, DriverError)



