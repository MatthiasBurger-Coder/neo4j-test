"""Domain node model for neutral addresses."""

from dataclasses import dataclass

from src.application.domain.addresses.model.geo_location import GeoLocation


@dataclass(slots=True)
class Address:
    """Represents an addressable place without external semantic meaning."""

    id: str
    house_number: str
    geo_location: GeoLocation | None = None

    def has_geo_location(self) -> bool:
        """Return whether this address includes explicit coordinates."""
        return self.geo_location is not None
