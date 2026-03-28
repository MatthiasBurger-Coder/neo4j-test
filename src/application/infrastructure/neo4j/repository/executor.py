"""Transactional Neo4j repository executor with logging and error translation."""

from time import perf_counter
from typing import Mapping, Protocol, TypeVar

from neo4j import ManagedTransaction, Query
from neo4j.exceptions import DriverError, Neo4jError

from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.contracts import Neo4jResultProjector
from src.application.infrastructure.neo4j.repository.error_translation import Neo4jRepositoryErrorTranslator
from src.application.infrastructure.neo4j.repository.logging import Neo4jOperationLogger
from src.application.infrastructure.neo4j.repository.operation import (
    Neo4jRepositoryOperationContext,
    Neo4jRepositoryOperationContextFactory,
)
from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.application.infrastructure.neo4j.repository.statement import CypherStatement
from src.application.infrastructure.neo4j.repository.strategy import (
    Neo4jTransactionExecutionStrategy,
    default_transaction_strategies,
)


class Neo4jSessionProviderProtocol(Protocol):
    """Abstraction for opening access-mode-specific Neo4j sessions."""

    database: str

    def open_session(self, access_mode: Neo4jAccessMode): ...


TResult = TypeVar("TResult")


class Neo4jRepositoryExecutor:
    """Coordinates session lifecycle, transaction strategy, logging, and errors."""

    def __init__(
        self,
        session_provider: Neo4jSessionProviderProtocol,
        *,
        context_factory: Neo4jRepositoryOperationContextFactory | None = None,
        operation_logger: Neo4jOperationLogger | None = None,
        error_translator: Neo4jRepositoryErrorTranslator | None = None,
        transaction_strategies: Mapping[Neo4jAccessMode, Neo4jTransactionExecutionStrategy[Neo4jExecutionResult]] | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._context_factory = context_factory or Neo4jRepositoryOperationContextFactory(
            database_name=session_provider.database
        )
        self._operation_logger = operation_logger or Neo4jOperationLogger(
            LoggerFactory.get_logger(self.__class__.__name__)
        )
        self._error_translator = error_translator or Neo4jRepositoryErrorTranslator()
        self._transaction_strategies = dict(transaction_strategies or default_transaction_strategies())

    def execute_read(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TResult],
    ) -> TResult:
        """Execute and project a read-side repository statement."""
        return self._execute(
            repository_name=repository_name,
            operation_name=operation_name,
            statement=statement,
            result_projector=result_projector,
            access_mode=Neo4jAccessMode.READ,
        )

    def execute_write(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TResult],
    ) -> TResult:
        """Execute and project a write-side repository statement."""
        return self._execute(
            repository_name=repository_name,
            operation_name=operation_name,
            statement=statement,
            result_projector=result_projector,
            access_mode=Neo4jAccessMode.WRITE,
        )

    def _execute(
        self,
        *,
        repository_name: str,
        operation_name: str,
        statement: CypherStatement,
        result_projector: Neo4jResultProjector[TResult],
        access_mode: Neo4jAccessMode,
    ) -> TResult:
        context = self._context_factory.create(
            repository_name=repository_name,
            operation_name=operation_name,
            access_mode=access_mode,
            statement_name=statement.name,
        )
        started_at = self._operation_logger.start_timer()
        self._operation_logger.log_started(context, statement)

        execution_result = self._execute_statement(statement=statement, context=context, started_at=started_at)
        return self._project_result(
            context=context,
            started_at=started_at,
            execution_result=execution_result,
            result_projector=result_projector,
        )

    def _execute_statement(
        self,
        *,
        statement: CypherStatement,
        context: Neo4jRepositoryOperationContext,
        started_at: float,
    ) -> Neo4jExecutionResult:
        transaction_strategy = self._transaction_strategies[context.access_mode]

        try:
            with self._session_provider.open_session(context.access_mode) as session:
                return transaction_strategy.execute(
                    session,
                    lambda transaction: self._run_statement(
                        transaction=transaction,
                        statement=statement,
                        context=context,
                    ),
                )
        except (Neo4jError, DriverError, OSError) as error:
            duration_ms = self._duration_ms(started_at)
            self._operation_logger.log_failed(
                context,
                duration_ms=duration_ms,
                failure_stage="execution",
                error=error,
            )
            translated_error = self._error_translator.translate(
                context=context,
                failure_stage="execution",
            )
            raise translated_error from error

    def _project_result(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        started_at: float,
        execution_result: Neo4jExecutionResult,
        result_projector: Neo4jResultProjector[TResult],
    ) -> TResult:
        try:
            projected_result = result_projector.project(execution_result)
        except Exception as error:
            duration_ms = self._duration_ms(started_at)
            self._operation_logger.log_failed(
                context,
                duration_ms=duration_ms,
                failure_stage="projection",
                error=error,
            )
            translated_error = self._error_translator.translate(
                context=context,
                failure_stage="projection",
            )
            raise translated_error from error

        duration_ms = self._duration_ms(started_at)
        self._operation_logger.log_succeeded(
            context,
            duration_ms=duration_ms,
            record_count=execution_result.record_count,
        )
        return projected_result

    def _run_statement(
        self,
        *,
        transaction: ManagedTransaction,
        statement: CypherStatement,
        context: Neo4jRepositoryOperationContext,
    ) -> Neo4jExecutionResult:
        query = Query(
            statement.cypher,
            metadata={
                "correlation_id": context.correlation_id,
                "repository_name": context.repository_name,
                "operation_name": context.operation_name,
                "statement_name": context.statement_name,
            },
        )
        query_result = transaction.run(query, statement.parameters)
        keys = tuple(query_result.keys())
        records = tuple(record.data() for record in query_result)
        summary = query_result.consume()
        counters = summary.counters

        return Neo4jExecutionResult(
            statement_name=statement.name,
            records=records,
            keys=keys,
            counters=Neo4jQueryCounters(
                nodes_created=counters.nodes_created,
                nodes_deleted=counters.nodes_deleted,
                relationships_created=counters.relationships_created,
                relationships_deleted=counters.relationships_deleted,
                properties_set=counters.properties_set,
                labels_added=counters.labels_added,
                labels_removed=counters.labels_removed,
                indexes_added=counters.indexes_added,
                indexes_removed=counters.indexes_removed,
                constraints_added=counters.constraints_added,
                constraints_removed=counters.constraints_removed,
                contains_updates=counters.contains_updates,
                contains_system_updates=counters.contains_system_updates,
            ),
            query_type=summary.query_type,
            database=getattr(summary, "database", None),
        )

    @staticmethod
    def _duration_ms(started_at: float) -> float:
        return (perf_counter() - started_at) * 1000
