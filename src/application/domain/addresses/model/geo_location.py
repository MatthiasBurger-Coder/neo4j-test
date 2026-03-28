from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoLocation:
    latitude: float
    longitude: float