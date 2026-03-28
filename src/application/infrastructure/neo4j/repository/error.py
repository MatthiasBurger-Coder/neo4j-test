"""Infrastructure-specific Neo4j repository exceptions."""

from src.application.infrastructure.neo4j.repository.operation import Neo4jRepositoryOperationContext


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
    ) -> None:
        super().__init__(
            f"{message} | repository={context.repository_name} | operation={context.operation_name} | "
            f"mode={context.access_mode.value} | statement={context.statement_name} | "
            f"database={context.database_name} | correlation_id={context.correlation_id} | "
            f"stage={failure_stage}"
        )
        self.context = context
        self.failure_stage = failure_stage


class Neo4jReadRepositoryError(Neo4jRepositoryError):
    """Raised for read-side repository failures."""


class Neo4jWriteRepositoryError(Neo4jRepositoryError):
    """Raised for write-side repository failures."""
