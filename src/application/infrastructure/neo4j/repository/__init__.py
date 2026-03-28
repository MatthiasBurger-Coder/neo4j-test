"""Reusable Neo4j repository foundation for read and write adapters."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.application.infrastructure.neo4j.repository.adapter import (
        Neo4jReadRepositoryAdapter,
        Neo4jWriteRepositoryAdapter,
    )
    from src.application.infrastructure.neo4j.repository.contracts import (
        CypherStatementBuilder,
        Neo4jRepositoryExecutorProtocol,
        Neo4jResultProjector,
    )
    from src.application.infrastructure.neo4j.repository.error import (
        Neo4jReadRepositoryError,
        Neo4jRepositoryConfigurationError,
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
    "Neo4jRepositoryConfigurationError",
    "Neo4jRepositoryExecutorProtocol",
    "Neo4jRepositoryError",
    "Neo4jRepositoryExecutor",
    "Neo4jResultProjector",
    "Neo4jWriteRepositoryAdapter",
    "Neo4jWriteRepositoryError",
]


_LAZY_EXPORTS = {
    "CypherStatement": ("src.application.infrastructure.neo4j.repository.statement", "CypherStatement"),
    "CypherStatementBuilder": ("src.application.infrastructure.neo4j.repository.contracts", "CypherStatementBuilder"),
    "CypherStatementTemplate": ("src.application.infrastructure.neo4j.repository.statement", "CypherStatementTemplate"),
    "Neo4jExecutionResult": ("src.application.infrastructure.neo4j.repository.result", "Neo4jExecutionResult"),
    "Neo4jQueryCounters": ("src.application.infrastructure.neo4j.repository.result", "Neo4jQueryCounters"),
    "Neo4jReadRepositoryAdapter": ("src.application.infrastructure.neo4j.repository.adapter", "Neo4jReadRepositoryAdapter"),
    "Neo4jReadRepositoryError": ("src.application.infrastructure.neo4j.repository.error", "Neo4jReadRepositoryError"),
    "Neo4jRepositoryConfigurationError": (
        "src.application.infrastructure.neo4j.repository.error",
        "Neo4jRepositoryConfigurationError",
    ),
    "Neo4jRepositoryExecutor": ("src.application.infrastructure.neo4j.repository.executor", "Neo4jRepositoryExecutor"),
    "Neo4jRepositoryExecutorProtocol": (
        "src.application.infrastructure.neo4j.repository.contracts",
        "Neo4jRepositoryExecutorProtocol",
    ),
    "Neo4jRepositoryError": ("src.application.infrastructure.neo4j.repository.error", "Neo4jRepositoryError"),
    "Neo4jResultProjector": ("src.application.infrastructure.neo4j.repository.contracts", "Neo4jResultProjector"),
    "Neo4jWriteRepositoryAdapter": ("src.application.infrastructure.neo4j.repository.adapter", "Neo4jWriteRepositoryAdapter"),
    "Neo4jWriteRepositoryError": ("src.application.infrastructure.neo4j.repository.error", "Neo4jWriteRepositoryError"),
}


def __getattr__(name: str) -> Any:
    """Resolve exports lazily to avoid premature driver-bound import cascades."""
    try:
        module_path, attribute_name = _LAZY_EXPORTS[name]
    except KeyError as error:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'") from error

    module = import_module(module_path)
    attribute = getattr(module, attribute_name)
    globals()[name] = attribute
    return attribute
