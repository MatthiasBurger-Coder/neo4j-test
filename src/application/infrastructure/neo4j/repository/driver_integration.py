"""Driver-specific Neo4j integration points isolated from the reusable repository base."""

from collections.abc import Mapping

from src.application.infrastructure.neo4j.repository.contracts import (
    Neo4jExecutionFailureClassifierProtocol,
    Neo4jQueryFactoryProtocol,
)


class Neo4jDriverQueryFactory(Neo4jQueryFactoryProtocol):
    """Builds driver-native query objects only when execution actually needs them."""

    def create(self, *, cypher: str, metadata: Mapping[str, object]) -> object:
        from neo4j import Query

        return Query(cypher, metadata=dict(metadata))


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
