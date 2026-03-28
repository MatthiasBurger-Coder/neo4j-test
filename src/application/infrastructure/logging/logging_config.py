import logging
import sys


class LoggingConfig:
    @staticmethod
    def configure(level: int = logging.INFO) -> None:
        root_logger = logging.getLogger()

        if root_logger.handlers:
            root_logger.handlers.clear()

        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        root_logger.setLevel(level)
        root_logger.addHandler(handler)

        logging.info("Logging configuration completed")

    @staticmethod
    def shutdown() -> None:
        logging.info("Shutting down logging configuration")
        logging.shutdown()
