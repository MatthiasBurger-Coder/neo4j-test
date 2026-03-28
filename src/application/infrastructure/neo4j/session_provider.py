from neo4j import Driver, READ_ACCESS, Session, WRITE_ACCESS

from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.neo4j.config import Neo4jConfig
from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.registry import Neo4jAccessModeRegistry


class Neo4jSessionProvider:
    def __init__(self, driver: Driver, config: Neo4jConfig) -> None:
        self._driver = driver
        self._config = config
        self._logger = LoggerFactory.get_logger(self.__class__.__name__)
        self._driver_access_modes = Neo4jAccessModeRegistry(
            registry_name=f"{self.__class__.__name__} driver access modes",
            entries={
                Neo4jAccessMode.READ: READ_ACCESS,
                Neo4jAccessMode.WRITE: WRITE_ACCESS,
            },
        )

    @property
    def database(self) -> str:
        return self._config.database

    def open_session(self, access_mode: Neo4jAccessMode) -> Session:
        self._logger.debug(
            "Opening Neo4j session for database=%s mode=%s",
            self._config.database,
            access_mode.value,
        )
        return self._driver.session(
            database=self._config.database,
            default_access_mode=self._driver_access_modes.get(access_mode),
        )

    def close(self) -> None:
        self._logger.info("Closing Neo4j driver")
        self._driver.close()
        self._logger.info("Neo4j driver closed successfully")
