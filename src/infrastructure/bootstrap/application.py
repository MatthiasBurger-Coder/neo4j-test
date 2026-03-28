"""Application composition root."""

import logging

from src.adapters.outbound.persistence.neo4j.repository.executor import Neo4jRepositoryExecutor
from src.adapters.outbound.persistence.neo4j.repository.operation import Neo4jRepositoryOperationContextFactory
from src.infrastructure.context.correlation_id import CorrelationIdContext
from src.infrastructure.http.config import HttpServerConfig
from src.infrastructure.http.server import WsgiHttpServer
from src.infrastructure.logging.logger_factory import LoggerFactory
from src.infrastructure.logging.logging_config import LoggingConfig
from src.infrastructure.neo4j.config import Neo4jConfig
from src.infrastructure.neo4j.connection_factory import Neo4jConnectionFactory
from src.infrastructure.neo4j.session_provider import Neo4jSessionProvider
from src.infrastructure.bootstrap.application_context import ApplicationContext
from src.infrastructure.bootstrap.application_repositories import create_application_repositories
from src.infrastructure.bootstrap.application_services import create_application_services
from src.infrastructure.bootstrap.http_api import create_http_api
from src.infrastructure.bootstrap.application_runtime import ApplicationRuntime


class Application:
    """Bootstraps the runtime and exposes only application-facing entry points."""

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
        repository_executor = Neo4jRepositoryExecutor(
            session_provider,
            context_factory=Neo4jRepositoryOperationContextFactory(
                database_name=session_provider.database,
                correlation_id_supplier=CorrelationIdContext.get,
            ),
            logger=LoggerFactory.get_logger(Neo4jRepositoryExecutor.__name__),
        )

        self._runtime = ApplicationRuntime.from_resources(session_provider)
        repositories = create_application_repositories(repository_executor=repository_executor)
        services = create_application_services(repositories=repositories)
        self._context = ApplicationContext(
            repositories=repositories,
            services=services,
            http_api=create_http_api(services=services),
            logger=logger,
        )

        logger.info("Application started successfully")
        return self._context

    def stop(self) -> None:
        if self._context is None or self._runtime is None:
            return

        self._context.logger.info("Stopping application")
        self._runtime.close()
        self._context.logger.info("Application stopped")
        self._runtime = None
        self._context = None
        LoggingConfig.shutdown()

    def run_http(self) -> None:
        """Start the JSON HTTP API and serve requests until interrupted."""
        context = self.start()
        server = WsgiHttpServer(
            config=HttpServerConfig.from_env(),
            wsgi_application=context.http_api,
            logger=LoggerFactory.get_logger(WsgiHttpServer.__name__),
        )

        try:
            server.serve_forever()
        finally:
            server.close()
            self.stop()



