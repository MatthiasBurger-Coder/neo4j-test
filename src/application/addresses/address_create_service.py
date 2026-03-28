"""Application service for address create operations."""

import logging
from typing import Callable
from uuid import uuid4

from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_create_port import AddressCreatePort
from src.application.addresses.address_write_port import AddressWriteError, AddressWritePort
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.node_id import NodeId


class AddressCreateValidationError(ValueError):
    """Raised when address creation input violates domain constraints."""


class AddressCreateOperationError(RuntimeError):
    """Raised when address creation fails for technical reasons."""


class AddressCreateService(AddressCreatePort):
    """Coordinates address create use cases through the outbound write port."""

    def __init__(
        self,
        address_write_port: AddressWritePort,
        *,
        logger: logging.Logger | None = None,
        id_generator: Callable[[], str] | None = None,
    ) -> None:
        self._address_write_port = address_write_port
        self._logger = logger or logging.getLogger(self.__class__.__name__)
        self._id_generator = id_generator or _generate_address_id

    def create_address(self, command: AddressCreateCommand) -> Address:
        """Create and persist a domain address from the incoming command."""
        self._logger.info("Address create started | operation=create_address")

        try:
            address = Address(
                id=NodeId(self._id_generator()),
                house_number=command.house_number,
                geo_location=_GEO_LOCATION_FACTORIES.get(
                    (command.latitude is None, command.longitude is None),
                    _raise_incomplete_geo_location,
                )(command.latitude, command.longitude),
            )
        except ValueError as error:
            self._logger.warning(
                "Address create rejected | operation=create_address | error=%s",
                error,
            )
            raise AddressCreateValidationError(str(error)) from error

        try:
            created_address = self._address_write_port.create_address(address)
        except AddressWriteError as error:
            self._logger.error(
                "Address create failed | operation=create_address | error=%s",
                error,
            )
            raise AddressCreateOperationError("Address could not be created") from error

        self._logger.info(
            "Address create succeeded | operation=create_address | address_id=%s",
            created_address.id.value,
        )
        return created_address


def _generate_address_id() -> str:
    return str(uuid4())


def _return_no_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation | None:
    del latitude, longitude
    return None


def _return_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation:
    if latitude is None or longitude is None:
        raise ValueError("Geo location requires both latitude and longitude")
    return GeoLocation(latitude=latitude, longitude=longitude)


def _raise_incomplete_geo_location(latitude: float | None, longitude: float | None) -> GeoLocation | None:
    raise ValueError(
        "Address geo location must provide both latitude and longitude or neither "
        f"(latitude={latitude!r}, longitude={longitude!r})"
    )


_GEO_LOCATION_FACTORIES = {
    (True, True): _return_no_geo_location,
    (False, False): _return_geo_location,
}
