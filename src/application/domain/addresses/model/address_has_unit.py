"""Domain relationship model connecting addresses and structured address units."""

from dataclasses import dataclass

from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressHasUnit:
    """Represents the relationship stating that an address has a structured unit."""

    id: str
    address_id: str
    address_unit_id: str
    trace_context: TraceContext | None = None
