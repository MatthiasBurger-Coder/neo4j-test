import logging

from src.application.infrastructure.neo4j.addresses.address_by_id_repository import Neo4jAddressByIdRepository
from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.logging.logging_config import LoggingConfig
from src.application.infrastructure.neo4j.config import Neo4jConfig
from src.application.infrastructure.neo4j.connection_factory import Neo4jConnectionFactory
from src.application.infrastructure.neo4j.repository.executor import Neo4jRepositoryExecutor
from src.application.infrastructure.neo4j.session_provider import Neo4jSessionProvider
from src.bootstrap.application_context import ApplicationContext
from src.bootstrap.application_repositories import AddressRepositories, ApplicationRepositories
from src.bootstrap.application_runtime import ApplicationRuntime


class Application:
    def __init__(self) -> None:
        self._context: ApplicationContext | None = None
        self._runtime: ApplicationRuntime | None = None

    def start(self) -> ApplicationContext:
        if self._context is not None:
            raise RuntimeError("Application is already started")

        LoggingConfig.configure(logging.INFO)

        logger = LoggerFactory.get_logger(self.__class__.__name__)
        logger.info("Starting application")

        config = Neo4jConfig.from_env()
        connection_factory = Neo4jConnectionFactory(config)
        driver = connection_factory.create_driver()
        session_provider = Neo4jSessionProvider(driver, config)
        repository_executor = Neo4jRepositoryExecutor(session_provider)
        repositories = ApplicationRepositories(
            addresses=AddressRepositories(
                by_id=Neo4jAddressByIdRepository(repository_executor),
            )
        )
        self._runtime = ApplicationRuntime(session_provider=session_provider)

        self._context = ApplicationContext(
            repositories=repositories,
            logger=logger,
        )

        logger.info("Application started successfully")
        return self._context

    def stop(self) -> None:
        if self._context is None or self._runtime is None:
            return

        self._context.logger.info("Stopping application")
        self._runtime.session_provider.close()
        self._context.logger.info("Application stopped")
        self._runtime = None
        self._context = None
        LoggingConfig.shutdown()
