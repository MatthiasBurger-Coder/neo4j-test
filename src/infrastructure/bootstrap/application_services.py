"""Application service wiring exposed by the bootstrap context."""

from dataclasses import dataclass

from src.application.addresses.address_create_port import AddressCreatePort
from src.application.addresses.address_create_service import AddressCreateService
from src.application.addresses.address_query_service import AddressQueryService
from src.application.addresses.address_read_port import AddressReadPort
from src.infrastructure.bootstrap.application_repositories import ApplicationRepositories
from src.infrastructure.logging.logger_factory import LoggerFactory


@dataclass(frozen=True, slots=True)
class AddressServices:
    """Provides address-related application services."""

    query: AddressReadPort
    create: AddressCreatePort


@dataclass(frozen=True, slots=True)
class ApplicationServices:
    """Groups application services exposed by the running application."""

    addresses: AddressServices


def create_application_services(*, repositories: ApplicationRepositories) -> ApplicationServices:
    """Create the application service bundle from wired repositories."""
    return ApplicationServices(
        addresses=AddressServices(
            query=AddressQueryService(
                repositories.addresses.read,
                logger=LoggerFactory.get_logger(AddressQueryService.__name__),
            ),
            create=AddressCreateService(
                repositories.addresses.write,
                logger=LoggerFactory.get_logger(AddressCreateService.__name__),
            )
        )
    )
