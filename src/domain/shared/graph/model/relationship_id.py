"""Typed identity value object for graph relationships."""

from dataclasses import dataclass

from src.domain.shared.validation import require_non_blank_text


@dataclass(frozen=True, slots=True)
class RelationshipId:
    """Immutable typed identifier for relationship concepts in the graph domain."""

    value: str

    def __post_init__(self) -> None:
        """Ensure the wrapped identifier value is not blank."""
        object.__setattr__(
            self,
            "value",
            require_non_blank_text(owner=self.__class__.__name__, field_name="value", value=self.value),
        )

    def __str__(self) -> str:
        """Return the raw identifier value for readable diagnostics."""
        return self.value



