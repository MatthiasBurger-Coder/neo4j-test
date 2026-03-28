"""Plain execution result models detached from Neo4j driver primitives."""

from dataclasses import dataclass
from typing import Any, Mapping


CypherRow = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class Neo4jQueryCounters:
    """Captures relevant mutation counters from a Neo4j statement execution."""

    nodes_created: int = 0
    nodes_deleted: int = 0
    relationships_created: int = 0
    relationships_deleted: int = 0
    properties_set: int = 0
    labels_added: int = 0
    labels_removed: int = 0
    indexes_added: int = 0
    indexes_removed: int = 0
    constraints_added: int = 0
    constraints_removed: int = 0
    contains_updates: bool = False
    contains_system_updates: bool = False


@dataclass(frozen=True, slots=True)
class Neo4jExecutionResult:
    """Provides a testable and driver-agnostic result shape for projectors."""

    statement_name: str
    records: tuple[CypherRow, ...]
    keys: tuple[str, ...]
    counters: Neo4jQueryCounters
    query_type: str | None = None
    database: str | None = None

    @property
    def record_count(self) -> int:
        """Return the number of rows materialized for the executed statement."""
        return len(self.records)
