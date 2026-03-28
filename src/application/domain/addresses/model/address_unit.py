"""Domain node model for structured address units."""

from dataclasses import dataclass

from src.application.domain.addresses.model.address_unit_type import AddressUnitType


@dataclass(slots=True)
class AddressUnit:
    """Represents a structured address unit as an independent node."""

    id: str
    unit_type: AddressUnitType
    value: str
