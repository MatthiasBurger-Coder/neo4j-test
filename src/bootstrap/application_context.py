from dataclasses import dataclass
import logging

from src.application.infrastructure.neo4j.config import Neo4jConfig
from src.application.infrastructure.neo4j.session_provider import Neo4jSessionProvider


@dataclass(frozen=True)
class ApplicationContext:
    config: Neo4jConfig
    session_provider: Neo4jSessionProvider
    logger: logging.Logger