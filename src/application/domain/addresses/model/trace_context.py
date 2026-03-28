"""Technical-neutral trace metadata for domain relationships."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TraceContext:
    """Carries correlation metadata without introducing infrastructure concerns."""

    correlation_id: str | None = None
    causation_id: str | None = None
    source_system: str | None = None
    source_channel: str | None = None
