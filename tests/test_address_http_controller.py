"""Unit tests for the address HTTP controller."""

import unittest

from src.adapters.inbound.http.address_controller import AddressHttpController
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
            )
        )

        response = controller.get_addresses()

        self.assertEqual(200, response.status_code)
        self.assertEqual("addr-1", response.payload[0]["id"])
        self.assertEqual(52.52, response.payload[0]["geo_location"]["latitude"])

    def test_get_address_by_id_returns_not_found_response(self) -> None:
        controller = AddressHttpController(_FakeAddressReadService(address=None))

        response = controller.get_address_by_id("missing-address")

        self.assertEqual(404, response.status_code)
        self.assertEqual("address_not_found", response.payload["error"]["code"])

    def test_get_address_by_id_returns_bad_request_for_invalid_identifier(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(error=AddressQueryValidationError("Address id must not be blank"))
        )

        response = controller.get_address_by_id("   ")

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_address_id", response.payload["error"]["code"])

    def test_get_addresses_returns_internal_error_without_leaking_details(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(error=RuntimeError("database unavailable"))
        )

        response = controller.get_addresses()

        self.assertEqual(500, response.status_code)
        self.assertEqual("internal_error", response.payload["error"]["code"])
        self.assertEqual("Internal server error", response.payload["error"]["message"])


if __name__ == "__main__":
    unittest.main()
