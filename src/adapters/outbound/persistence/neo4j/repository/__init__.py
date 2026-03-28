"""Reusable Neo4j repository foundation for read and write adapters."""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from src.adapters.outbound.persistence.neo4j.repository.adapter import (
        Neo4jReadRepositoryAdapter,
        Neo4jWriteRepositoryAdapter,
    )
    from src.adapters.outbound.persistence.neo4j.repository.contracts import (
        CypherStatementBuilder,
        Neo4jRepositoryExecutorProtocol,
        Neo4jResultProjector,
    )
    from src.adapters.outbound.persistence.neo4j.repository.error import (
        Neo4jReadRepositoryError,
        Neo4jRepositoryConfigurationError,
        Neo4jRepositoryError,
        Neo4jWriteRepositoryError,
    )
    from src.adapters.outbound.persistence.neo4j.repository.executor import Neo4jRepositoryExecutor
    from src.adapters.outbound.persistence.neo4j.repository.result import Neo4jExecutionResult, Neo4jQueryCounters
    from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement, CypherStatementTemplate

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
    "CypherStatement": ("src.adapters.outbound.persistence.neo4j.repository.statement", "CypherStatement"),
    "CypherStatementBuilder": ("src.adapters.outbound.persistence.neo4j.repository.contracts", "CypherStatementBuilder"),
    "CypherStatementTemplate": ("src.adapters.outbound.persistence.neo4j.repository.statement", "CypherStatementTemplate"),
    "Neo4jExecutionResult": ("src.adapters.outbound.persistence.neo4j.repository.result", "Neo4jExecutionResult"),
    "Neo4jQueryCounters": ("src.adapters.outbound.persistence.neo4j.repository.result", "Neo4jQueryCounters"),
    "Neo4jReadRepositoryAdapter": ("src.adapters.outbound.persistence.neo4j.repository.adapter", "Neo4jReadRepositoryAdapter"),
    "Neo4jReadRepositoryError": ("src.adapters.outbound.persistence.neo4j.repository.error", "Neo4jReadRepositoryError"),
    "Neo4jRepositoryConfigurationError": (
        "src.adapters.outbound.persistence.neo4j.repository.error",
        "Neo4jRepositoryConfigurationError",
    ),
    "Neo4jRepositoryExecutor": ("src.adapters.outbound.persistence.neo4j.repository.executor", "Neo4jRepositoryExecutor"),
    "Neo4jRepositoryExecutorProtocol": (
        "src.adapters.outbound.persistence.neo4j.repository.contracts",
        "Neo4jRepositoryExecutorProtocol",
    ),
    "Neo4jRepositoryError": ("src.adapters.outbound.persistence.neo4j.repository.error", "Neo4jRepositoryError"),
    "Neo4jResultProjector": ("src.adapters.outbound.persistence.neo4j.repository.contracts", "Neo4jResultProjector"),
    "Neo4jWriteRepositoryAdapter": ("src.adapters.outbound.persistence.neo4j.repository.adapter", "Neo4jWriteRepositoryAdapter"),
    "Neo4jWriteRepositoryError": ("src.adapters.outbound.persistence.neo4j.repository.error", "Neo4jWriteRepositoryError"),
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



