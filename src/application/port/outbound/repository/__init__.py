"""Generic repository ports for application-facing persistence access."""

from src.application.port.outbound.repository.read_repository import ReadRepositoryPort
from src.application.port.outbound.repository.write_repository import WriteRepositoryPort

__all__ = ["ReadRepositoryPort", "WriteRepositoryPort"]
