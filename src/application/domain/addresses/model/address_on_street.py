"""Domain relationship model connecting addresses and streets."""

from dataclasses import dataclass

from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressOnStreet:
    """Represents the relationship stating that an address is on a street."""

    id: str
    address_id: str
    street_id: str
    trace_context: TraceContext | None = None
