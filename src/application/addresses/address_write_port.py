"""Outbound application port for address write operations."""

from abc import ABC, abstractmethod

from src.domain.addresses.model.address import Address


class AddressWriteError(RuntimeError):
    """Raised when the address write boundary fails technically."""


class AddressWritePort(ABC):
    """Defines write-side persistence required by address application services."""

    @abstractmethod
    def create_address(self, address: Address) -> Address:
        """Persist and return the created address."""
