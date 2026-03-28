"""Infrastructure-specific Neo4j repository exceptions."""

from src.application.infrastructure.neo4j.repository.operation import Neo4jRepositoryOperationContext
from src.application.infrastructure.validation import require_non_blank


class Neo4jRepositoryConfigurationError(RuntimeError):
    """Raised when repository infrastructure is configured incompletely or inconsistently."""


class Neo4jRepositoryError(RuntimeError):
    """Base error raised when the Neo4j repository infrastructure fails."""

    def __init__(
        self,
        *,
        message: str,
        context: Neo4jRepositoryOperationContext,
        failure_stage: str,
        technical_message: str,
    ) -> None:
        normalized_failure_stage = require_non_blank(
            owner=self.__class__.__name__,
            field_name="failure_stage",
            value=failure_stage,
        )
        normalized_technical_message = require_non_blank(
            owner=self.__class__.__name__,
            field_name="technical_message",
            value=technical_message,
        )
        super().__init__(
            f"{message} | repository={context.repository_name} | operation={context.operation_name} | "
            f"mode={context.access_mode.value} | statement={context.statement_name} | "
            f"database={context.database_name} | correlation_id={context.correlation_id} | "
            f"stage={normalized_failure_stage} | technical_error={normalized_technical_message}"
        )
        self.context = context
        self.failure_stage = normalized_failure_stage
        self.technical_message = normalized_technical_message


class Neo4jReadRepositoryError(Neo4jRepositoryError):
    """Raised for read-side repository failures."""


class Neo4jWriteRepositoryError(Neo4jRepositoryError):
    """Raised for write-side repository failures."""
