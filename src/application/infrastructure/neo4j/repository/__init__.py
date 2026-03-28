"""Reusable Neo4j repository foundation for read and write adapters."""

from src.application.infrastructure.neo4j.repository.adapter import Neo4jReadRepositoryAdapter, Neo4jWriteRepositoryAdapter
from src.application.infrastructure.neo4j.repository.contracts import (
    CypherStatementBuilder,
    Neo4jRepositoryExecutorProtocol,
    Neo4jResultProjector,
)
from src.application.infrastructure.neo4j.repository.error import (
    Neo4jReadRepositoryError,
    Neo4jRepositoryError,
    Neo4jWriteRepositoryError,
)
from src.application.infrastructure.neo4j.repository.executor import Neo4jRepositoryExecutor
from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
from src.application.infrastructure.neo4j.repository.statement import CypherStatement, CypherStatementTemplate

__all__ = [
    "CypherStatement",
    "CypherStatementBuilder",
    "CypherStatementTemplate",
    "Neo4jExecutionResult",
    "Neo4jQueryCounters",
    "Neo4jReadRepositoryAdapter",
    "Neo4jReadRepositoryError",
    "Neo4jRepositoryExecutorProtocol",
    "Neo4jRepositoryError",
    "Neo4jRepositoryExecutor",
    "Neo4jResultProjector",
    "Neo4jWriteRepositoryAdapter",
    "Neo4jWriteRepositoryError",
]
