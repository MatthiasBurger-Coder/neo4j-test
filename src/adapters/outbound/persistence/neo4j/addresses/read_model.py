"""Infrastructure read models for Neo4j-backed address queries."""

from dataclasses import dataclass

from src.domain.shared.validation import require_non_blank_text


@dataclass(frozen=True, slots=True)
class AddressReadModel:
    """Captures the persisted shape needed to reconstruct an address."""

    address_id: str
    house_number: str
    latitude: float | None = None
    longitude: float | None = None

    def __post_init__(self) -> None:
        """Validate required persisted values."""
        object.__setattr__(
            self,
            "address_id",
            require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="address_id",
                value=self.address_id,
            ),
        )
        object.__setattr__(
            self,
            "house_number",
            require_non_blank_text(
                owner=self.__class__.__name__,
                field_name="house_number",
                value=self.house_number,
            ),
        )
