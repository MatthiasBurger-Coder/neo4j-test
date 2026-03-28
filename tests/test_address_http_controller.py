"""Unit tests for the address HTTP controller."""

import unittest

from src.adapters.inbound.http.address_controller import AddressHttpController
from src.adapters.inbound.http.request import HttpRequest
from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateValidationError,
)
from src.application.addresses.address_query_service import AddressQueryValidationError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.node_id import NodeId


class _FakeAddressReadService:
    def __init__(
        self,
        *,
        address: Address | None = None,
        addresses: tuple[Address, ...] = (),
        error: Exception | None = None,
    ) -> None:
        self._address = address
        self._addresses = addresses
        self._error = error

    def get_address_by_id(self, address_id: str) -> Address | None:
        del address_id
        if self._error is not None:
            raise self._error
        return self._address

    def get_all_addresses(self) -> tuple[Address, ...]:
        if self._error is not None:
            raise self._error
        return self._addresses


class _FakeAddressCreateService:
    def __init__(self, *, address: Address | None = None, error: Exception | None = None) -> None:
        self._address = address
        self._error = error
        self.last_command: AddressCreateCommand | None = None

    def create_address(self, command: AddressCreateCommand) -> Address:
        self.last_command = command
        if self._error is not None:
            raise self._error
        if self._address is None:
            raise AssertionError("A created address must be configured for create controller tests")
        return self._address


class AddressHttpControllerTest(unittest.TestCase):
    def test_get_addresses_returns_json_payload(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(
                addresses=(
                    Address(
                        id=NodeId("addr-1"),
                        house_number="42A",
                        geo_location=GeoLocation(latitude=52.52, longitude=13.405),
                    ),
                )
            ),
            _FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        response = controller.get_addresses()

        self.assertEqual(200, response.status_code)
        self.assertEqual("addr-1", response.payload[0]["id"])
        self.assertEqual(52.52, response.payload[0]["geo_location"]["latitude"])

    def test_get_address_by_id_returns_not_found_response(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(address=None),
            _FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        response = controller.get_address_by_id("missing-address")

        self.assertEqual(404, response.status_code)
        self.assertEqual("address_not_found", response.payload["error"]["code"])

    def test_get_address_by_id_returns_bad_request_for_invalid_identifier(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(error=AddressQueryValidationError("Address id must not be blank")),
            _FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        response = controller.get_address_by_id("   ")

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_address_id", response.payload["error"]["code"])

    def test_get_addresses_returns_internal_error_without_leaking_details(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(error=RuntimeError("database unavailable")),
            _FakeAddressCreateService(address=_create_address("addr-created", "55")),
        )

        response = controller.get_addresses()

        self.assertEqual(500, response.status_code)
        self.assertEqual("internal_error", response.payload["error"]["code"])
        self.assertEqual("Internal server error", response.payload["error"]["message"])

    def test_create_address_returns_created_response(self) -> None:
        create_service = _FakeAddressCreateService(address=_create_address("addr-1", "42A"))
        controller = AddressHttpController(_FakeAddressReadService(), create_service)

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"house_number":"42A","geo_location":{"latitude":52.52,"longitude":13.405}}',
            )
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("addr-1", response.payload["id"])
        self.assertEqual("42A", create_service.last_command.house_number)
        self.assertEqual(52.52, create_service.last_command.latitude)

    def test_create_address_returns_bad_request_for_invalid_json(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(address=_create_address("addr-1", "42A")),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"house_number":',
            )
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_json", response.payload["error"]["code"])

    def test_create_address_returns_unprocessable_entity_for_domain_validation_error(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(error=AddressCreateValidationError("Address house_number must not be blank")),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"house_number":"   "}',
            )
        )

        self.assertEqual(422, response.status_code)
        self.assertEqual("invalid_address", response.payload["error"]["code"])

    def test_create_address_returns_internal_error_for_technical_failure(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(error=AddressCreateOperationError("Address could not be created")),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"house_number":"42A"}',
            )
        )

        self.assertEqual(500, response.status_code)
        self.assertEqual("internal_error", response.payload["error"]["code"])


def _create_address(address_id: str, house_number: str) -> Address:
    return Address(id=NodeId(address_id), house_number=house_number)


if __name__ == "__main__":
    unittest.main()
