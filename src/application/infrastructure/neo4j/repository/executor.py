"""Transactional Neo4j repository executor with centralized logging and isolated driver integration."""

import logging
from time import perf_counter
from typing import Mapping, TypeVar

from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.contracts import (
    Neo4jExecutionFailureClassifierProtocol,
    Neo4jQueryFactoryProtocol,
    Neo4jRepositoryExecutorProtocol,
    Neo4jResultCursorProtocol,
    Neo4jResultProjector,
    Neo4jSessionProviderProtocol,
    Neo4jTransactionProtocol,
)
from src.application.infrastructure.neo4j.repository.driver_integration import (
    Neo4jDriverExecutionFailureClassifier,
    Neo4jDriverQueryFactory,
)
from src.application.infrastructure.neo4j.repository.error_translation import Neo4jRepositoryErrorTranslator
from src.application.infrastructure.neo4j.repository.operation import (
    Neo4jRepositoryOperationContext,
    Neo4jRepositoryOperationContextFactory,
)
from src.application.infrastructure.neo4j.repository.registry import Neo4jAccessModeRegistry
from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.application.infrastructure.neo4j.repository.statement import CypherStatement
from src.application.infrastructure.neo4j.repository.strategy import (
    Neo4jTransactionExecutionStrategy,
    default_transaction_strategies,
)


TResult = TypeVar("TResult")


class Neo4jRepositoryExecutor(Neo4jRepositoryExecutorProtocol):
    """Coordinates session lifecycle, transaction strategy, logging, and error translation."""

    def __init__(
        self,
        session_provider: Neo4jSessionProviderProtocol,
        *,
        context_factory: Neo4jRepositoryOperationContextFactory | None = None,
        error_translator: Neo4jRepositoryErrorTranslator | None = None,
        logger: logging.Logger | None = None,
        query_factory: Neo4jQueryFactoryProtocol | None = None,
        failure_classifier: Neo4jExecutionFailureClassifierProtocol | None = None,
        transaction_strategies: Mapping[
            Neo4jAccessMode,
            Neo4jTransactionExecutionStrategy[Neo4jExecutionResult],
        ]
        | None = None,
    ) -> None:
        self._session_provider = session_provider
        self._context_factory = context_factory or Neo4jRepositoryOperationContextFactory(
            database_name=session_provider.database
        )
        self._error_translator = error_translator or Neo4jRepositoryErrorTranslator()
        self._logger = logger or LoggerFactory.get_logger(self.__class__.__name__)
        self._query_factory = query_factory or Neo4jDriverQueryFactory()
        self._failure_classifier = failure_classifier or Neo4jDriverExecutionFailureClassifier()
        self._transaction_strategies = Neo4jAccessModeRegistry(
            registry_name=f"{self.__class__.__name__} transaction strategies",
            entries=transaction_strategies or default_transaction_strategies(),
        )

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
        started_at = perf_counter()
        self._log_started(context=context, statement=statement)

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
        transaction_strategy = self._transaction_strategies.get(context.access_mode)

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
        except Exception as error:
            if not self._failure_classifier.is_execution_failure(error):
                raise

            self._log_failed(
                context=context,
                duration_ms=self._duration_ms(started_at),
                failure_stage="execution",
                error=error,
            )
            raise self._error_translator.translate(
                context=context,
                failure_stage="execution",
                technical_message=self._describe_error(error),
            ) from error

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
            self._log_failed(
                context=context,
                duration_ms=self._duration_ms(started_at),
                failure_stage="projection",
                error=error,
            )
            raise self._error_translator.translate(
                context=context,
                failure_stage="projection",
                technical_message=self._describe_error(error),
            ) from error

        self._log_succeeded(
            context=context,
            duration_ms=self._duration_ms(started_at),
            record_count=execution_result.record_count,
        )
        return projected_result

    def _run_statement(
        self,
        *,
        transaction: Neo4jTransactionProtocol,
        statement: CypherStatement,
        context: Neo4jRepositoryOperationContext,
    ) -> Neo4jExecutionResult:
        query = self._query_factory.create(
            cypher=statement.cypher,
            metadata={
                "correlation_id": context.correlation_id,
                "repository_name": context.repository_name,
                "operation_name": context.operation_name,
                "statement_name": context.statement_name,
            },
        )
        query_result = transaction.run(query, statement.parameters)
        return self._materialize_result(query_result=query_result, statement_name=statement.name)

    def _materialize_result(
        self,
        *,
        query_result: Neo4jResultCursorProtocol,
        statement_name: str,
    ) -> Neo4jExecutionResult:
        keys = tuple(query_result.keys())
        records = tuple(record.data() for record in query_result)
        summary = query_result.consume()
        counters = summary.counters

        return Neo4jExecutionResult(
            statement_name=statement_name,
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

    def _log_started(self, *, context: Neo4jRepositoryOperationContext, statement: CypherStatement) -> None:
        self._logger.info(
            "Neo4j operation started | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | parameter_keys=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            statement.name,
            context.database_name,
            tuple(statement.parameters.keys()),
        )

    def _log_succeeded(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        duration_ms: float,
        record_count: int,
    ) -> None:
        self._logger.info(
            "Neo4j operation succeeded | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | duration_ms=%.3f | record_count=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            context.statement_name,
            context.database_name,
            duration_ms,
            record_count,
        )

    def _log_failed(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        duration_ms: float,
        failure_stage: str,
        error: Exception,
    ) -> None:
        self._logger.error(
            "Neo4j operation failed | repository=%s | operation=%s | mode=%s | statement=%s | database=%s | duration_ms=%.3f | stage=%s | error_type=%s | error=%s",
            context.repository_name,
            context.operation_name,
            context.access_mode.value,
            context.statement_name,
            context.database_name,
            duration_ms,
            failure_stage,
            error.__class__.__name__,
            error,
        )

    @staticmethod
    def _describe_error(error: BaseException) -> str:
        error_message = str(error).strip()
        return (
            f"{error.__class__.__name__}: {error_message}"
            if error_message != ""
            else error.__class__.__name__
        )

    @staticmethod
    def _duration_ms(started_at: float) -> float:
        return (perf_counter() - started_at) * 1000
