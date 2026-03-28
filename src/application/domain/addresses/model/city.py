"""Domain node model for cities."""

from dataclasses import dataclass


@dataclass(slots=True)
class City:
    """Represents a city as an independent domain node."""

    id: str
    name: str
    country: str
    postal_code: str | None = None
