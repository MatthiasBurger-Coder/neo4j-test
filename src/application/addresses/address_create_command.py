"""Application command for address creation use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AddressCreateCommand:
    """Carries normalized external input for address creation."""

    house_number: str
    latitude: float | None = None
    longitude: float | None = None
