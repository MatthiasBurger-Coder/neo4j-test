import logging
import sys

from src.infrastructure.logging.correlation_id_log_filter import CorrelationIdLogFilter


class LoggingConfig:
    @staticmethod
    def configure(level: int = logging.INFO) -> None:
        root_logger = logging.getLogger()

        if root_logger.handlers:
            root_logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | correlation_id=%(correlation_id)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(CorrelationIdLogFilter())

        root_logger.setLevel(level)
        root_logger.addHandler(handler)

        logging.info("Logging configuration completed")

    @staticmethod
    def shutdown() -> None:
        logging.info("Shutting down logging configuration")
        logging.shutdown()



