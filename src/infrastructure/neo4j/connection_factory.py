"""Factory for driver-backed Neo4j connections."""

from typing import TYPE_CHECKING

from src.infrastructure.logging.logger_factory import LoggerFactory
from src.infrastructure.neo4j.config import Neo4jConfig

if TYPE_CHECKING:
    from neo4j import Driver


class Neo4jConnectionFactory:
    """Creates verified Neo4j drivers from validated infrastructure configuration."""

    def __init__(self, config: Neo4jConfig) -> None:
        self._config = config
        self._logger = LoggerFactory.get_logger(self.__class__.__name__)

    def create_driver(self) -> "Driver":
        from neo4j import GraphDatabase

        self._logger.info("Creating Neo4j driver for uri=%s database=%s", self._config.uri, self._config.database)

        driver = GraphDatabase.driver(
            self._config.uri,
            auth=(self._config.username, self._config.password),
            max_connection_lifetime=self._config.max_connection_lifetime,
            max_connection_pool_size=self._config.max_connection_pool_size,
            connection_acquisition_timeout=self._config.connection_acquisition_timeout,
        )

        driver.verify_connectivity()
        self._logger.info("Neo4j connectivity verified successfully")
        return driver



