"""Centralized logging for Neo4j repository operations."""

from time import perf_counter
import logging

from src.application.infrastructure.neo4j.repository.operation import Neo4jRepositoryOperationContext
from src.application.infrastructure.neo4j.repository.statement import CypherStatement


class Neo4jOperationLogger:
    """Logs repository execution start, success, and failure with shared metadata."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def start_timer(self) -> float:
        """Provide a monotonic start time for duration tracking."""
        return perf_counter()

    def log_started(self, context: Neo4jRepositoryOperationContext, statement: CypherStatement) -> None:
        """Log the beginning of a database operation."""
        self._logger.info(
            "Neo4j operation started | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | correlation_id=%s | parameter_keys=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            statement.name,
            context.database_name,
            context.correlation_id,
            tuple(statement.parameters.keys()),
        )

    def log_succeeded(
        self,
        context: Neo4jRepositoryOperationContext,
        *,
        duration_ms: float,
        record_count: int,
    ) -> None:
        """Log a successful database operation."""
        self._logger.info(
            "Neo4j operation succeeded | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | correlation_id=%s | duration_ms=%.3f | record_count=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            context.statement_name,
            context.database_name,
            context.correlation_id,
            duration_ms,
            record_count,
        )

    def log_failed(
        self,
        context: Neo4jRepositoryOperationContext,
        *,
        duration_ms: float,
        failure_stage: str,
        error: Exception,
    ) -> None:
        """Log a failed database operation with execution context."""
        self._logger.error(
            "Neo4j operation failed | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | correlation_id=%s | duration_ms=%.3f | stage=%s | error_type=%s | error=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            context.statement_name,
            context.database_name,
            context.correlation_id,
            duration_ms,
            failure_stage,
            error.__class__.__name__,
            error,
        )
