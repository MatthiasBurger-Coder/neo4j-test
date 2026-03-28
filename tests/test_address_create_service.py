"""Unit tests for the address application create service."""

import unittest

from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateService,
    AddressCreateValidationError,
)
from src.application.addresses.address_write_port import AddressWriteError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.node_id import NodeId


class _FakeAddressWritePort:
    def __init__(self, *, created_address: Address | None = None, error: Exception | None = None) -> None:
        self._created_address = created_address
        self._error = error
        self.last_address: Address | None = None

    def create_address(self, address: Address) -> Address:
        self.last_address = address
        if self._error is not None:
            raise self._error
        if self._created_address is None:
            raise AssertionError("A created address must be configured for service tests")
        return self._created_address


class AddressCreateServiceTest(unittest.TestCase):
    def test_create_address_builds_domain_object_and_returns_created_address(self) -> None:
        created_address = Address(
            id=NodeId("addr-1"),
            house_number="42A",
            geo_location=GeoLocation(latitude=52.52, longitude=13.405),
        )
        write_port = _FakeAddressWritePort(created_address=created_address)
        service = AddressCreateService(write_port, id_generator=lambda: "addr-1")

        result = service.create_address(
            AddressCreateCommand(
                house_number="42A",
                latitude=52.52,
                longitude=13.405,
            )
        )

        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("addr-1", write_port.last_address.id.value)
        self.assertEqual("42A", write_port.last_address.house_number)
        self.assertEqual(52.52, write_port.last_address.geo_location.latitude)

    def test_create_address_raises_validation_error_for_blank_house_number(self) -> None:
        service = AddressCreateService(
            _FakeAddressWritePort(created_address=Address(id=NodeId("addr-1"), house_number="42A")),
            id_generator=lambda: "addr-1",
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(AddressCreateCommand(house_number="   "))

        self.assertIn("must not be blank", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_partial_geo_location(self) -> None:
        service = AddressCreateService(
            _FakeAddressWritePort(created_address=Address(id=NodeId("addr-1"), house_number="42A")),
            id_generator=lambda: "addr-1",
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(AddressCreateCommand(house_number="42A", latitude=52.52))

        self.assertIn("must provide both latitude and longitude or neither", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_invalid_geo_range(self) -> None:
        service = AddressCreateService(
            _FakeAddressWritePort(created_address=Address(id=NodeId("addr-1"), house_number="42A")),
            id_generator=lambda: "addr-1",
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(
                AddressCreateCommand(
                    house_number="42A",
                    latitude=120.0,
                    longitude=13.405,
                )
            )

        self.assertIn("latitude must be between -90.0 and 90.0", str(raised_error.exception))

    def test_create_address_raises_operation_error_for_write_failure(self) -> None:
        service = AddressCreateService(
            _FakeAddressWritePort(error=AddressWriteError("Address persistence failed")),
            id_generator=lambda: "addr-1",
        )

        with self.assertRaises(AddressCreateOperationError) as raised_error:
            service.create_address(AddressCreateCommand(house_number="42A"))

        self.assertEqual("Address could not be created", str(raised_error.exception))


if __name__ == "__main__":
    unittest.main()
