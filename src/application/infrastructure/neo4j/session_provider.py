from neo4j import Driver, Session

from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.neo4j.config import Neo4jConfig


class Neo4jSessionProvider:
    def __init__(self, driver: Driver, config: Neo4jConfig) -> None:
        self._driver = driver
        self._config = config
        self._logger = LoggerFactory.get_logger(self.__class__.__name__)

    def open_session(self) -> Session:
        self._logger.debug("Opening Neo4j session for database=%s", self._config.database)
        return self._driver.session(database=self._config.database)

    def close(self) -> None:
        self._logger.info("Closing Neo4j driver")
        self._driver.close()
        self._logger.info("Neo4j driver closed successfully")