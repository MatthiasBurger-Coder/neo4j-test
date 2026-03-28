"""Operational context metadata for Neo4j repository execution."""

from dataclasses import dataclass
from typing import Callable

from src.application.infrastructure.context.correlation_id import CorrelationIdContext
from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode


CorrelationIdSupplier = Callable[[], str]


@dataclass(frozen=True, slots=True)
class Neo4jRepositoryOperationContext:
    """Carries execution metadata used for logging, tracing, and errors."""

    repository_name: str
    operation_name: str
    access_mode: Neo4jAccessMode
    statement_name: str
    database_name: str
    correlation_id: str


class Neo4jRepositoryOperationContextFactory:
    """Creates validated operation contexts for repository executions."""

    def __init__(
        self,
        *,
        database_name: str,
        correlation_id_supplier: CorrelationIdSupplier = CorrelationIdContext.get,
    ) -> None:
        self._database_name = self._require_non_blank("database_name", database_name)
        self._correlation_id_supplier = correlation_id_supplier

    def create(
        self,
        *,
        repository_name: str,
        operation_name: str,
        access_mode: Neo4jAccessMode,
        statement_name: str,
    ) -> Neo4jRepositoryOperationContext:
        """Build a context object for a single repository operation."""
        return Neo4jRepositoryOperationContext(
            repository_name=self._require_non_blank("repository_name", repository_name),
            operation_name=self._require_non_blank("operation_name", operation_name),
            access_mode=access_mode,
            statement_name=self._require_non_blank("statement_name", statement_name),
            database_name=self._database_name,
            correlation_id=self._correlation_id_supplier(),
        )

    @staticmethod
    def _require_non_blank(field_name: str, value: str) -> str:
        normalized_value = value.strip()
        if normalized_value == "":
            raise ValueError(f"Neo4jRepositoryOperationContextFactory {field_name} must not be blank")
        return normalized_value
