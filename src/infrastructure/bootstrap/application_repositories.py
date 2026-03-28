"""Application-facing repository bundle exposed by the bootstrap context."""

from dataclasses import dataclass

from src.adapters.outbound.persistence.neo4j.addresses.address_read_adapter import (
    Neo4jAddressReadAdapter,
)
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jRepositoryExecutorProtocol
from src.domain.addresses.ports.address_read_repository import AddressReadRepositoryPort


@dataclass(frozen=True, slots=True)
class AddressRepositories:
    """Provides address-related repository entry points to the application."""

    read: AddressReadRepositoryPort


@dataclass(frozen=True, slots=True)
class ApplicationRepositories:
    """Groups concrete repository ports exposed to the running application."""

    addresses: AddressRepositories


def create_application_repositories(
    *,
    repository_executor: Neo4jRepositoryExecutorProtocol,
) -> ApplicationRepositories:
    """Create the application-facing repository bundle from infrastructure adapters."""
    return ApplicationRepositories(
        addresses=AddressRepositories(
            read=Neo4jAddressReadAdapter(repository_executor),
        )
    )



