"""Write-side persistence models for Neo4j address creation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateAddressWriteModel:
    """Represents the flattened write payload for a Neo4j address node."""

    address_id: str
    house_number: str
    latitude: float | None
    longitude: float | None
