"""Internal runtime resources owned by the application bootstrap."""

from dataclasses import dataclass

from src.application.infrastructure.neo4j.session_provider import Neo4jSessionProvider


@dataclass(frozen=True, slots=True)
class ApplicationRuntime:
    """Holds technical runtime resources that should not leak into the application context."""

    session_provider: Neo4jSessionProvider
