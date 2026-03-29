"""Unit tests for the address application create service."""

from datetime import datetime, timezone
import unittest

from src.application.addresses.address_context import AddressContextDraft, CreatedAddressContext
from src.application.addresses.address_create_command import (
    AddressAssignmentPayloadCommand,
    AddressCreateCommand,
    AddressPayloadCommand,
    AddressUnitHierarchyPayloadCommand,
    AddressUnitPayloadCommand,
    BuildingPayloadCommand,
    CityPayloadCommand,
    GeoLocationCommand,
    RelatedEntityPayloadCommand,
    StreetPayloadCommand,
)
from src.application.addresses.address_create_service import (
    AddressCreateOperationError,
    AddressCreateService,
    AddressCreateValidationError,
)
from src.application.addresses.address_write_port import AddressWriteError
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


class _FakeAddressWritePort:
    def __init__(self, *, created_context: CreatedAddressContext | None = None, error: Exception | None = None) -> None:
        self._created_context = created_context
        self._error = error
        self.last_context: AddressContextDraft | None = None

    def create_address(self, address_context: AddressContextDraft) -> CreatedAddressContext:
        self.last_context = address_context
        if self._error is not None:
            raise self._error
        if self._created_context is None:
            raise AssertionError("A created context must be configured for service tests")
        return self._created_context


class AddressCreateServiceTest(unittest.TestCase):
    def test_create_address_builds_validated_context_and_returns_result(self) -> None:
        write_port = _FakeAddressWritePort(created_context=_create_created_context())
        service = AddressCreateService(write_port)

        result = service.create_address(_create_full_command())

        self.assertEqual("addr-1", result.address.id.value)
        self.assertEqual("Town Hall", result.building.name)
        self.assertEqual("Marienplatz", write_port.last_context.street.name)
        self.assertEqual("Germany", write_port.last_context.city.country)
        self.assertEqual(AddressUnitType.ENTRANCE, write_port.last_context.units[0].unit_type)
        self.assertEqual("ENTRANCE:North", write_port.last_context.units[0].reference)
        self.assertEqual("FLOOR:3", write_port.last_context.unit_hierarchy[0].child_ref)
        self.assertEqual(RelatedEntityType.PERSON, write_port.last_context.assignments[0].related_entity.entity_type)
        self.assertEqual(AddressRelationType.RESIDENCE, write_port.last_context.assignments[0].relation_type)

    def test_create_address_raises_validation_error_for_invalid_unit_type(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            units=(AddressUnitPayloadCommand(unit_type="INVALID", value="North"),)
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("AddressUnitType", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_invalid_relation_type(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            assignments=(
                AddressAssignmentPayloadCommand(
                    related_entity=RelatedEntityPayloadCommand(entity_type="PERSON", entity_id="person-123"),
                    relation_type="INVALID",
                ),
            )
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("AddressRelationType", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_invalid_geo_range(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            address=AddressPayloadCommand(
                house_number="12A",
                geo_location=GeoLocationCommand(latitude=120.0, longitude=11.576124),
            )
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("latitude must be between -90.0 and 90.0", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_invalid_assignment_window(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            assignments=(
                AddressAssignmentPayloadCommand(
                    related_entity=RelatedEntityPayloadCommand(entity_type="PERSON", entity_id="person-123"),
                    relation_type="RESIDENCE",
                    valid_from="2024-02-01T00:00:00Z",
                    valid_to="2024-01-01T00:00:00Z",
                ),
            )
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("valid_to must not be earlier", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_unknown_unit_hierarchy_reference(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            unit_hierarchy=(
                AddressUnitHierarchyPayloadCommand(
                    parent_ref="ENTRANCE:North",
                    child_ref="ROOM:404",
                ),
            )
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("does not reference a declared unit", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_duplicate_units(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            units=(
                AddressUnitPayloadCommand(unit_type="ENTRANCE", value="North"),
                AddressUnitPayloadCommand(unit_type="ENTRANCE", value="North"),
            ),
            unit_hierarchy=(),
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("must be unique", str(raised_error.exception))

    def test_create_address_raises_validation_error_for_blank_house_number(self) -> None:
        service = AddressCreateService(_FakeAddressWritePort(created_context=_create_created_context()))
        command = _create_full_command(
            address=AddressPayloadCommand(house_number="   ")
        )

        with self.assertRaises(AddressCreateValidationError) as raised_error:
            service.create_address(command)

        self.assertIn("must not be blank", str(raised_error.exception))

    def test_create_address_raises_operation_error_for_write_failure(self) -> None:
        service = AddressCreateService(
            _FakeAddressWritePort(error=AddressWriteError("Address context persistence failed"))
        )

        with self.assertRaises(AddressCreateOperationError) as raised_error:
            service.create_address(_create_full_command())

        self.assertEqual("Address context could not be created", str(raised_error.exception))


def _create_full_command(
    *,
    address: AddressPayloadCommand | None = None,
    street: StreetPayloadCommand | None = None,
    city: CityPayloadCommand | None = None,
    building: BuildingPayloadCommand | None = None,
    units: tuple[AddressUnitPayloadCommand, ...] | None = None,
    unit_hierarchy: tuple[AddressUnitHierarchyPayloadCommand, ...] | None = None,
    assignments: tuple[AddressAssignmentPayloadCommand, ...] | None = None,
) -> AddressCreateCommand:
    return AddressCreateCommand(
        address=address
        or AddressPayloadCommand(
            house_number="12A",
            geo_location=GeoLocationCommand(latitude=48.137154, longitude=11.576124),
        ),
        street=street or StreetPayloadCommand(name="Marienplatz"),
        city=city or CityPayloadCommand(name="Munich", country="Germany", postal_code="80331"),
        building=building
        or BuildingPayloadCommand(
            name="Town Hall",
            geo_location=GeoLocationCommand(latitude=48.1372, longitude=11.5759),
        ),
        units=units
        or (
            AddressUnitPayloadCommand(unit_type="ENTRANCE", value="North"),
            AddressUnitPayloadCommand(unit_type="FLOOR", value="3"),
            AddressUnitPayloadCommand(unit_type="APARTMENT", value="12"),
        ),
        unit_hierarchy=unit_hierarchy
        or (
            AddressUnitHierarchyPayloadCommand(parent_ref="ENTRANCE:North", child_ref="FLOOR:3"),
            AddressUnitHierarchyPayloadCommand(parent_ref="FLOOR:3", child_ref="APARTMENT:12"),
        ),
        assignments=assignments
        or (
            AddressAssignmentPayloadCommand(
                related_entity=RelatedEntityPayloadCommand(entity_type="PERSON", entity_id="person-123"),
                relation_type="RESIDENCE",
                valid_from="2024-01-01T00:00:00Z",
                source="registry",
                note="Primary residence",
            ),
        ),
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
        AddressUnit(id=NodeId("unit-3"), unit_type=AddressUnitType.APARTMENT, value="12"),
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
            AddressHasUnit(id=RelationshipId("rel-address-unit-3"), address_id=address.id, address_unit_id=units[2].id),
        ),
        unit_hierarchy=(
            AddressUnitWithinUnit(
                id=RelationshipId("rel-unit-hierarchy-1"),
                parent_unit_id=units[0].id,
                child_unit_id=units[1].id,
            ),
            AddressUnitWithinUnit(
                id=RelationshipId("rel-unit-hierarchy-2"),
                parent_unit_id=units[1].id,
                child_unit_id=units[2].id,
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
                valid_to=None,
                source="registry",
                note="Primary residence",
            ),
        ),
    )


if __name__ == "__main__":
    unittest.main()
