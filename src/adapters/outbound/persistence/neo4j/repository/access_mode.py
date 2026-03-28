"""Internal repository access modes for Neo4j sessions and transactions."""

from enum import Enum


class Neo4jAccessMode(str, Enum):
    """Represents the transaction access mode for a repository operation."""

    READ = "read"
    WRITE = "write"

    @classmethod
    def all(cls) -> tuple["Neo4jAccessMode", ...]:
        """Return all defined access modes in declaration order."""
        return tuple(cls)



