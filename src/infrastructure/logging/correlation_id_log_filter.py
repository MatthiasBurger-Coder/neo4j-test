"""Logging filter that injects the active correlation ID into each log record."""

import logging

from src.infrastructure.context.correlation_id import CorrelationIdContext


class CorrelationIdLogFilter(logging.Filter):
    """Adds correlation ID data to log records for centralized observability."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Attach the current correlation ID to the outgoing log record."""
        record.correlation_id = CorrelationIdContext.get()
        return True



