"""Unit tests for the address HTTP controller."""

from datetime import datetime, timezone
import unittest

from src.adapters.inbound.http.address_controller import AddressHttpController
from src.adapters.inbound.http.request import HttpRequest
from src.application.addresses.address_context import CreatedAddressContext
from src.application.addresses.address_create_command import AddressCreateCommand
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateValidationError,
)
from src.application.addresses.address_query_service import AddressQueryValidationError
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.address_assignment import AddressAssignment
from src.domain.addresses.model.address_has_unit import AddressHasUnit
from src.domain.addresses.model.address_in_building import AddressInBuilding
from src.domain.addresses.model.address_on_street import AddressOnStreet
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit import AddressUnit
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.address_unit_within_unit import AddressUnitWithinUnit
from src.domain.addresses.model.building import Building
from src.domain.addresses.model.city import City
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef, RelatedEntityType
from src.domain.addresses.model.street import Street
from src.domain.addresses.model.street_in_city import StreetInCity
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId


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
    def __init__(self, *, context: CreatedAddressContext | None = None, error: Exception | None = None) -> None:
        self._context = context
        self._error = error
        self.last_command: AddressCreateCommand | None = None

    def create_address(self, command: AddressCreateCommand) -> CreatedAddressContext:
        self.last_command = command
        if self._error is not None:
            raise self._error
        if self._context is None:
            raise AssertionError("A created context must be configured for create controller tests")
        return self._context


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
            _FakeAddressCreateService(context=_create_created_context()),
        )

        response = controller.get_addresses()

        self.assertEqual(200, response.status_code)
        self.assertEqual("addr-1", response.payload[0]["id"])
        self.assertEqual(52.52, response.payload[0]["geo_location"]["latitude"])

    def test_get_address_by_id_returns_not_found_response(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(address=None),
            _FakeAddressCreateService(context=_create_created_context()),
        )

        response = controller.get_address_by_id("missing-address")

        self.assertEqual(404, response.status_code)
        self.assertEqual("address_not_found", response.payload["error"]["code"])

    def test_get_address_by_id_returns_bad_request_for_invalid_identifier(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(error=AddressQueryValidationError("Address id must not be blank")),
            _FakeAddressCreateService(context=_create_created_context()),
        )

        response = controller.get_address_by_id("   ")

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_address_id", response.payload["error"]["code"])

    def test_create_address_returns_created_response_for_full_context(self) -> None:
        create_service = _FakeAddressCreateService(context=_create_created_context())
        controller = AddressHttpController(_FakeAddressReadService(), create_service)

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=_full_request_body(),
            )
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual("addr-1", response.payload["address"]["id"])
        self.assertEqual("street-1", response.payload["street"]["id"])
        self.assertEqual("building-1", response.payload["building"]["id"])
        self.assertEqual("ENTRANCE", response.payload["units"][0]["unit_type"])
        self.assertEqual("PERSON", response.payload["assignments"][0]["related_entity"]["entity_type"])
        self.assertEqual("12A", create_service.last_command.address.house_number)
        self.assertEqual("Marienplatz", create_service.last_command.street.name)

    def test_create_address_returns_bad_request_for_invalid_json(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(context=_create_created_context()),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=b'{"address":',
            )
        )

        self.assertEqual(400, response.status_code)
        self.assertEqual("invalid_json", response.payload["error"]["code"])

    def test_create_address_returns_unsupported_media_type(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(context=_create_created_context()),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "text/plain"},
                body=_full_request_body(),
            )
        )

        self.assertEqual(415, response.status_code)
        self.assertEqual("unsupported_media_type", response.payload["error"]["code"])

    def test_create_address_returns_unprocessable_content_for_validation_error(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(error=AddressCreateValidationError("AddressUnitType invalid")),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=_full_request_body(),
            )
        )

        self.assertEqual(422, response.status_code)
        self.assertEqual("invalid_address", response.payload["error"]["code"])

    def test_create_address_returns_internal_error_for_technical_failure(self) -> None:
        controller = AddressHttpController(
            _FakeAddressReadService(),
            _FakeAddressCreateService(error=AddressCreateOperationError("Address context could not be created")),
        )

        response = controller.create_address(
            HttpRequest(
                method="POST",
                path="/addresses",
                headers={"content-type": "application/json"},
                body=_full_request_body(),
            )
        )

        self.assertEqual(500, response.status_code)
        self.assertEqual("internal_error", response.payload["error"]["code"])


def _full_request_body() -> bytes:
    return (
        b'{"address":{"house_number":"12A","geo_location":{"latitude":48.137154,"longitude":11.576124}},'
        b'"street":{"name":"Marienplatz"},'
        b'"city":{"name":"Munich","country":"Germany","postal_code":"80331"},'
        b'"building":{"name":"Town Hall","geo_location":{"latitude":48.1372,"longitude":11.5759}},'
        b'"units":[{"unit_type":"ENTRANCE","value":"North"},{"unit_type":"FLOOR","value":"3"}],'
        b'"unit_hierarchy":[{"parent_ref":"ENTRANCE:North","child_ref":"FLOOR:3"}],'
        b'"assignments":[{"related_entity":{"entity_type":"PERSON","entity_id":"person-123"},'
        b'"relation_type":"RESIDENCE","valid_from":"2024-01-01T00:00:00Z","source":"registry","note":"Primary residence"}]}'
    )


def _create_created_context() -> CreatedAddressContext:
    address = Address(
        id=NodeId("addr-1"),
        house_number="12A",
        geo_location=GeoLocation(latitude=48.137154, longitude=11.576124),
    )
    street = Street(id=NodeId("street-1"), name="Marienplatz")
    city = City(id=NodeId("city-1"), name="Munich", country="Germany", postal_code="80331")
    building = Building(
        id=NodeId("building-1"),
        name="Town Hall",
        geo_location=GeoLocation(latitude=48.1372, longitude=11.5759),
    )
    units = (
        AddressUnit(id=NodeId("unit-1"), unit_type=AddressUnitType.ENTRANCE, value="North"),
        AddressUnit(id=NodeId("unit-2"), unit_type=AddressUnitType.FLOOR, value="3"),
    )
    return CreatedAddressContext(
        address=address,
        street=street,
        city=city,
        address_on_street=AddressOnStreet(
            id=RelationshipId("rel-address-street-1"),
            address_id=address.id,
            street_id=street.id,
        ),
        street_in_city=StreetInCity(
            id=RelationshipId("rel-street-city-1"),
            street_id=street.id,
            city_id=city.id,
        ),
        building=building,
        address_in_building=AddressInBuilding(
            id=RelationshipId("rel-address-building-1"),
            address_id=address.id,
            building_id=building.id,
        ),
        units=units,
        address_has_units=(
            AddressHasUnit(id=RelationshipId("rel-address-unit-1"), address_id=address.id, address_unit_id=units[0].id),
            AddressHasUnit(id=RelationshipId("rel-address-unit-2"), address_id=address.id, address_unit_id=units[1].id),
        ),
        unit_hierarchy=(
            AddressUnitWithinUnit(
                id=RelationshipId("rel-unit-hierarchy-1"),
                parent_unit_id=units[0].id,
                child_unit_id=units[1].id,
            ),
        ),
        assignments=(
            AddressAssignment(
                id=RelationshipId("rel-assignment-1"),
                related_entity=RelatedEntityRef(
                    entity_type=RelatedEntityType.PERSON,
                    entity_id=NodeId("person-123"),
                ),
                address_id=address.id,
                relation_type=AddressRelationType.RESIDENCE,
                valid_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
                source="registry",
                note="Primary residence",
            ),
        ),
    )


if __name__ == "__main__":
    unittest.main()
