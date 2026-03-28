from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from src.application.domain.addresses.model.geo_location import GeoLocation


@dataclass(slots=True)
class Address:
    street: str
    house_number: str
    postal_code: str
    city: str
    country: str
    geo_location: Optional[GeoLocation] = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def full_address(self) -> str:
        parts = [
            f"{self.street} {self.house_number}".strip(),
            f"{self.postal_code} {self.city}".strip(),
            self.country.strip(),
        ]
        return ", ".join(part for part in parts if part.strip())