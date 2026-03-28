"""Infrastructure-level trace metadata used for observability across boundaries."""

from dataclasses import dataclass

from src.infrastructure.validation import require_optional_non_blank


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Carries optional technical trace identifiers for logs and integrations."""

    correlation_id: str | None = None
    causation_id: str | None = None
    source_system: str | None = None
    source_channel: str | None = None

    def __post_init__(self) -> None:
        """Validate trace metadata fields when values are provided."""
        object.__setattr__(
            self,
            "correlation_id",
            require_optional_non_blank(owner=self.__class__.__name__, field_name="correlation_id", value=self.correlation_id),
        )
        object.__setattr__(
            self,
            "causation_id",
            require_optional_non_blank(owner=self.__class__.__name__, field_name="causation_id", value=self.causation_id),
        )
        object.__setattr__(
            self,
            "source_system",
            require_optional_non_blank(owner=self.__class__.__name__, field_name="source_system", value=self.source_system),
        )
        object.__setattr__(
            self,
            "source_channel",
            require_optional_non_blank(owner=self.__class__.__name__, field_name="source_channel", value=self.source_channel),
        )



