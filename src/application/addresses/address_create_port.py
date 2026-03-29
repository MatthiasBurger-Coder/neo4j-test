"""Inbound application port for address create use cases."""

from abc import ABC, abstractmethod

from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_context import CreatedAddressContext


class AddressCreatePort(ABC):
    """Defines the application-facing address creation contract."""

    @abstractmethod
    def create_address(self, command: AddressCreateCommand) -> CreatedAddressContext:
        """Create a new address context from external input."""
