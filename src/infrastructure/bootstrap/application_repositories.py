"""Application-facing repository bundle exposed by the bootstrap context."""

from dataclasses import dataclass

from src.domain.addresses.ports.address_by_id_repository import AddressByIdRepositoryPort
from src.adapters.outbound.persistence.neo4j.addresses.address_by_id_repository import Neo4jAddressByIdRepository
from src.adapters.outbound.persistence.neo4j.repository.contracts import Neo4jRepositoryExecutorProtocol


@dataclass(frozen=True, slots=True)
class AddressRepositories:
    """Provides address-related repository entry points to the application."""

    by_id: AddressByIdRepositoryPort


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
            by_id=Neo4jAddressByIdRepository(repository_executor),
        )
    )



