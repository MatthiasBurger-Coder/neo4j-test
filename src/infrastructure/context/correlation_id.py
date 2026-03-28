"""Infrastructure helper for storing request correlation IDs in context-local state."""

import uuid
from contextvars import ContextVar


_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="-")


class CorrelationIdContext:
    """Provides technical correlation ID lifecycle operations for runtime context."""

    @staticmethod
    def get() -> str:
        return _correlation_id.get()

    @staticmethod
    def set(correlation_id: str) -> None:
        _correlation_id.set(correlation_id)

    @staticmethod
    def generate() -> str:
        correlation_id = str(uuid.uuid4())
        _correlation_id.set(correlation_id)
        return correlation_id

    @staticmethod
    def clear() -> None:
        _correlation_id.set("-")

    @staticmethod
    def is_valid() -> bool:
        return _correlation_id.get() != "-"



