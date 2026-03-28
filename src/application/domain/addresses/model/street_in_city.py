"""Domain relationship model connecting streets and cities."""

from dataclasses import dataclass

from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class StreetInCity:
    """Represents the relationship stating that a street belongs to a city."""

    id: str
    street_id: str
    city_id: str
    trace_context: TraceContext | None = None
