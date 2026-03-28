"""Unit tests for the address application query service."""

import unittest

from src.application.addresses.address_query_service import (
    AddressQueryService,
    AddressQueryValidationError,
)
from src.domain.addresses.model.address import Address
from src.domain.addresses.ports.address_read_repository import AddressReadCriteria
from src.domain.shared.graph.model.node_id import NodeId


class _FakeAddressReadRepository:
    def __init__(
        self,
        *,
        address_by_id: Address | None = None,
        addresses: tuple[Address, ...] = (),
    ) -> None:
        self._address_by_id = address_by_id
        self._addresses = addresses
        self.last_address_id: NodeId | None = None

    def find_by_id(self, address_id: NodeId) -> Address | None:
        self.last_address_id = address_id
        return self._address_by_id

    def find_all(self) -> tuple[Address, ...]:
        return self._addresses

    def find_by_criteria(self, criteria: AddressReadCriteria) -> tuple[Address, ...]:
        del criteria
        return self._addresses


class AddressQueryServiceTest(unittest.TestCase):
    def test_get_address_by_id_returns_domain_address(self) -> None:
        repository = _FakeAddressReadRepository(address_by_id=_create_address("addr-1", "42A"))
        service = AddressQueryService(repository)

        result = service.get_address_by_id("addr-1")

        self.assertEqual("addr-1", result.id.value)
        self.assertEqual("addr-1", repository.last_address_id.value)

    def test_get_address_by_id_raises_validation_error_for_blank_identifier(self) -> None:
        service = AddressQueryService(_FakeAddressReadRepository())

        with self.assertRaises(AddressQueryValidationError) as raised_error:
            service.get_address_by_id("   ")

        self.assertIn("must not be blank", str(raised_error.exception))

    def test_get_all_addresses_returns_repository_collection(self) -> None:
        service = AddressQueryService(
            _FakeAddressReadRepository(
                addresses=(
                    _create_address("addr-1", "42A"),
                    _create_address("addr-2", "43"),
                )
            )
        )

        result = service.get_all_addresses()

        self.assertEqual(("addr-1", "addr-2"), tuple(address.id.value for address in result))


def _create_address(address_id: str, house_number: str) -> Address:
    return Address(id=NodeId(address_id), house_number=house_number)


if __name__ == "__main__":
    unittest.main()
