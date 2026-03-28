"""Application-facing port for read-oriented repositories."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TReadRequest = TypeVar("TReadRequest", contravariant=True)
TReadResult = TypeVar("TReadResult", covariant=True)


class ReadRepositoryPort(ABC, Generic[TReadRequest, TReadResult]):
    """Defines the application contract for read-side repositories."""

    @abstractmethod
    def execute(self, request_model: TReadRequest) -> TReadResult:
        """Execute a read-side repository operation."""
