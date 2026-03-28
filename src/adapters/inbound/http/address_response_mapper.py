"""Maps address domain objects to JSON-serializable HTTP payloads."""

from src.domain.addresses.model.address import Address
from src.domain.addresses.model.geo_location import GeoLocation


class AddressHttpResponseMapper:
    """Converts address domain objects into JSON-friendly payloads."""

    def map_one(self, address: Address) -> dict[str, object]:
        """Map a single address to a JSON-ready dictionary."""
        return {
            "id": address.id.value,
            "house_number": address.house_number,
            "geo_location": _GEO_LOCATION_PAYLOAD_FACTORIES[address.geo_location is None](address.geo_location),
        }

    def map_many(self, addresses: tuple[Address, ...]) -> list[dict[str, object]]:
        """Map multiple addresses to a JSON-ready list."""
        return [self.map_one(address) for address in addresses]


def _return_no_geo_location_payload(geo_location: GeoLocation | None) -> None:
    del geo_location
    return None


def _return_geo_location_payload(geo_location: GeoLocation | None) -> dict[str, float]:
    if geo_location is None:
        raise ValueError("Geo location payload requires a geo location value")
    return {
        "latitude": geo_location.latitude,
        "longitude": geo_location.longitude,
    }


_GEO_LOCATION_PAYLOAD_FACTORIES = {
    True: _return_no_geo_location_payload,
    False: _return_geo_location_payload,
}
