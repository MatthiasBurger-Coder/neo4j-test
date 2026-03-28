"""Operational context metadata for Neo4j repository execution."""

from dataclasses import dataclass
from typing import Callable

from src.adapters.outbound.persistence.neo4j.repository.access_mode import Neo4jAccessMode
from src.domain.shared.validation import require_non_blank_text


CorrelationIdSupplier = Callable[[], str]


def _default_correlation_id_supplier() -> str:
    return "-"


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
        correlation_id_supplier: CorrelationIdSupplier = _default_correlation_id_supplier,
    ) -> None:
        self._database_name = require_non_blank_text(
            owner=self.__class__.__name__,
            field_name="database_name",
            value=database_name,
        )
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
            repository_name=require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="repository_name",
                value=repository_name,
            ),
            operation_name=require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="operation_name",
                value=operation_name,
            ),
            access_mode=access_mode,
            statement_name=require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="statement_name",
                value=statement_name,
            ),
            database_name=self._database_name,
            correlation_id=require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="correlation_id",
                value=self._correlation_id_supplier(),
            ),
        )



