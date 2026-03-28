"""Domain node model for streets."""

from dataclasses import dataclass


@dataclass(slots=True)
class Street:
    """Represents a street as an independent domain node."""

    id: str
    name: str
