import logging

from src.application.context.application_context import ApplicationContext
from src.application.infrastructure.logging.logger_factory import LoggerFactory
from src.application.infrastructure.logging.logging_config import LoggingConfig
from src.application.infrastructure.neo4j.config import Neo4jConfig
from src.application.infrastructure.neo4j.connection_factory import Neo4jConnectionFactory
from src.application.infrastructure.neo4j.session_provider import Neo4jSessionProvider


class Application:
    def __init__(self) -> None:
        self._context: ApplicationContext | None = None

    def start(self) -> ApplicationContext:
        LoggingConfig.configure(logging.INFO)

        logger = LoggerFactory.get_logger(self.__class__.__name__)
        logger.info("Starting application")

        config = Neo4jConfig.from_env()
        connection_factory = Neo4jConnectionFactory(config)
        driver = connection_factory.create_driver()
        session_provider = Neo4jSessionProvider(driver, config)

        self._context = ApplicationContext(
            config=config,
            session_provider=session_provider,
            logger=logger,
        )

        logger.info("Application started successfully")
        return self._context

    def stop(self) -> None:
        if self._context is None:
            return

        self._context.logger.info("Stopping application")
        self._context.session_provider.close()
        self._context.logger.info("Application stopped")

def main() -> None:
    app = Application()
    context = app.start()

    try:
        context.logger.info("Program is running")
        # start actual workflow here
    finally:
        app.stop()


if __name__ == "__main__":
    main()