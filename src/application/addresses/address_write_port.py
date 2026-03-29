"""Outbound application port for address-context write operations."""

from abc import ABC, abstractmethod

from src.application.addresses.address_context import AddressContextDraft, CreatedAddressContext


class AddressWriteError(RuntimeError):
    """Raised when the address write boundary fails technically."""


class AddressWritePort(ABC):
    """Defines write-side persistence required by address application services."""

    @abstractmethod
    def create_address(self, address_context: AddressContextDraft) -> CreatedAddressContext:
        """Persist and return the created or merged address context."""
