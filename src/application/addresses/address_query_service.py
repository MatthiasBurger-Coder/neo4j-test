"""Application service for address read operations."""

import logging

from src.application.addresses.address_read_port import AddressReadPort
from src.domain.addresses.model.address import Address
from src.domain.addresses.ports.address_read_repository import AddressReadRepositoryPort
from src.domain.shared.graph.model.node_id import NodeId


class AddressQueryValidationError(ValueError):
    """Raised when external address query input is invalid for the use case."""


class AddressQueryService(AddressReadPort):
    """Coordinates address read use cases through the outbound read repository port."""

    def __init__(
        self,
        address_read_repository: AddressReadRepositoryPort,
        *,
        logger: logging.Logger | None = None,
    ) -> None:
        self._address_read_repository = address_read_repository
        self._logger = logger or logging.getLogger(self.__class__.__name__)

    def get_address_by_id(self, address_id: str) -> Address | None:
        """Load a single address after validating the external identifier."""
        self._logger.info("Address query started | operation=get_address_by_id | address_id=%s", address_id)

        try:
            node_id = NodeId(address_id)
        except ValueError as error:
            self._logger.warning(
                "Address query rejected | operation=get_address_by_id | address_id=%s | error=%s",
                address_id,
                error,
            )
            raise AddressQueryValidationError(str(error)) from error

        address = self._address_read_repository.find_by_id(node_id)
        self._logger.info(
            "Address query succeeded | operation=get_address_by_id | address_id=%s | found=%s",
            address_id,
            address is not None,
        )
        return address

    def get_all_addresses(self) -> tuple[Address, ...]:
        """Load all addresses through the read repository port."""
        self._logger.info("Address query started | operation=get_all_addresses")
        addresses = self._address_read_repository.find_all()
        self._logger.info(
            "Address query succeeded | operation=get_all_addresses | count=%s",
            len(addresses),
        )
        return addresses
