"""Domain node model for buildings."""

from dataclasses import dataclass

from src.application.domain.addresses.model.geo_location import GeoLocation


@dataclass(slots=True)
class Building:
    """Represents a building as an independent domain node."""

    id: str
    name: str | None
    geo_location: GeoLocation
