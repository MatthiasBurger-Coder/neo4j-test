"""Inbound application port for address read use cases."""

from abc import ABC, abstractmethod

from src.domain.addresses.model.address import Address


class AddressReadPort(ABC):
    """Defines the application-facing address read contract."""

    @abstractmethod
    def get_address_by_id(self, address_id: str) -> Address | None:
        """Load a single address for the provided external identifier."""

    @abstractmethod
    def get_all_addresses(self) -> tuple[Address, ...]:
        """Load all available addresses."""
