from neo4j import Driver, GraphDatabase

from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.neo4j.config import Neo4jConfig


class Neo4jConnectionFactory:
    def __init__(self, config: Neo4jConfig) -> None:
        self._config = config
        self._logger = LoggerFactory.get_logger(self.__class__.__name__)

    def create_driver(self) -> Driver:
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