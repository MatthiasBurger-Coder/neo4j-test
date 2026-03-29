"""Maps address domain and application models to JSON-serializable HTTP payloads."""

from datetime import datetime

from src.application.addresses.address_context import CreatedAddressContext
from src.domain.addresses.model.address import Address
from src.domain.addresses.model.address_assignment import AddressAssignment
from src.domain.addresses.model.address_unit import AddressUnit
from src.domain.addresses.model.building import Building
from src.domain.addresses.model.city import City
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.street import Street


class AddressHttpResponseMapper:
    """Converts address domain and create-result objects into JSON-friendly payloads."""

    def map_one(self, address: Address) -> dict[str, object]:
        """Map a single address to a JSON-ready dictionary."""
        return {
            "id": address.id.value,
            "house_number": address.house_number,
            "geo_location": _map_geo_location(address.geo_location),
        }

    def map_many(self, addresses: tuple[Address, ...]) -> list[dict[str, object]]:
        """Map multiple addresses to a JSON-ready list."""
        return [self.map_one(address) for address in addresses]

    def map_created_context(self, address_context: CreatedAddressContext) -> dict[str, object]:
        """Map the created address context to the HTTP create-response payload."""
        return {
            "address": self.map_one(address_context.address),
            "street": _map_street(address_context.street),
            "city": _map_city(address_context.city),
            "building": _map_building(address_context.building),
            "units": [_map_unit(unit) for unit in address_context.units],
            "unit_hierarchy": [
                {
                    "id": relationship.id.value,
                    "parent_unit_id": relationship.parent_unit_id.value,
                    "child_unit_id": relationship.child_unit_id.value,
                }
                for relationship in address_context.unit_hierarchy
            ],
            "assignments": [_map_assignment(assignment) for assignment in address_context.assignments],
        }


def _map_street(street: Street) -> dict[str, object]:
    return {
        "id": street.id.value,
        "name": street.name,
    }


def _map_city(city: City) -> dict[str, object]:
    return {
        "id": city.id.value,
        "name": city.name,
        "country": city.country,
        "postal_code": city.postal_code,
    }


def _map_building(building: Building | None) -> dict[str, object] | None:
    if building is None:
        return None

    return {
        "id": building.id.value,
        "name": building.name,
        "geo_location": _map_geo_location(building.geo_location),
    }


def _map_unit(unit: AddressUnit) -> dict[str, object]:
    return {
        "id": unit.id.value,
        "unit_type": unit.unit_type.value,
        "value": unit.value,
    }


def _map_assignment(assignment: AddressAssignment) -> dict[str, object]:
    return {
        "id": assignment.id.value,
        "relation_type": assignment.relation_type.value,
        "related_entity": {
            "entity_type": assignment.related_entity.entity_type.value,
            "entity_id": assignment.related_entity.entity_id.value,
        },
        "valid_from": _map_datetime(assignment.valid_from),
        "valid_to": _map_datetime(assignment.valid_to),
        "source": assignment.source,
        "note": assignment.note,
    }


def _map_datetime(value: datetime | None) -> str | None:
    return None if value is None else value.isoformat().replace("+00:00", "Z")


def _map_geo_location(geo_location: GeoLocation | None) -> dict[str, float] | None:
    if geo_location is None:
        return None
    return {
        "latitude": geo_location.latitude,
        "longitude": geo_location.longitude,
    }
