"""Application-facing port for write-oriented repositories."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar


TWriteRequest = TypeVar("TWriteRequest", contravariant=True)
TWriteResult = TypeVar("TWriteResult", covariant=True)


class WriteRepositoryPort(ABC, Generic[TWriteRequest, TWriteResult]):
    """Defines the application contract for write-side repositories."""

    @abstractmethod
    def execute(self, request_model: TWriteRequest) -> TWriteResult:
        """Execute a write-side repository operation."""
