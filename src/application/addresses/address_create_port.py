"""Inbound application port for address create use cases."""

from abc import ABC, abstractmethod

from src.application.addresses.address_create_command import AddressCreateCommand
from src.domain.addresses.model.address import Address


class AddressCreatePort(ABC):
    """Defines the application-facing address creation contract."""

    @abstractmethod
    def create_address(self, command: AddressCreateCommand) -> Address:
        """Create a new address from external input."""
