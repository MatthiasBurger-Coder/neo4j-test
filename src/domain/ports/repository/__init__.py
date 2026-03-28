"""Generic repository ports for application-facing persistence access."""

from src.domain.ports.repository.read_repository import ReadRepositoryPort
from src.domain.ports.repository.write_repository import WriteRepositoryPort

__all__ = ["ReadRepositoryPort", "WriteRepositoryPort"]



