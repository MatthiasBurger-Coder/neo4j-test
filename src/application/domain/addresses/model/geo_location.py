"""Value object for geographical coordinates."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoLocation:
    """Represents a precise point on Earth."""

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Validate coordinate ranges according to geographic bounds."""
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90.0 and 90.0")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180.0 and 180.0")
