"""Typed identity value object for graph nodes."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NodeId:
    """Immutable typed identifier for node concepts in the graph domain."""

    value: str

    def __post_init__(self) -> None:
        """Ensure the wrapped identifier value is not blank."""
        if not self.value or self.value.strip() == "":
            raise ValueError("NodeId value must not be blank")

    def __str__(self) -> str:
        """Return the raw identifier value for readable diagnostics."""
        return self.value
