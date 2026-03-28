"""Infrastructure-level trace metadata used for observability across boundaries."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Carries optional technical trace identifiers for logs and integrations."""

    correlation_id: str | None = None
    causation_id: str | None = None
    source_system: str | None = None
    source_channel: str | None = None

    def __post_init__(self) -> None:
        """Validate trace metadata fields when values are provided."""
        self._validate_optional_non_blank("correlation_id", self.correlation_id)
        self._validate_optional_non_blank("causation_id", self.causation_id)
        self._validate_optional_non_blank("source_system", self.source_system)
        self._validate_optional_non_blank("source_channel", self.source_channel)

    @staticmethod
    def _validate_optional_non_blank(field_name: str, value: str | None) -> None:
        if value is not None and value.strip() == "":
            raise ValueError(f"TraceContext {field_name} must not be blank when provided")
