import logging


class LoggerFactory:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)

    @staticmethod
    def shutdown() -> None:
        logging.info("Shutting down logging configuration")
        root_logger = logging.getLogger()
        root_logger.handlers = []