"""Application-facing repository bundle exposed by the bootstrap context."""

from dataclasses import dataclass

from src.application.domain.addresses.port.address_by_id_repository import AddressByIdRepositoryPort


@dataclass(frozen=True, slots=True)
class AddressRepositories:
    """Provides address-related repository entry points to the application."""

    by_id: AddressByIdRepositoryPort


@dataclass(frozen=True, slots=True)
class ApplicationRepositories:
    """Groups concrete repository ports exposed to the running application."""

    addresses: AddressRepositories
