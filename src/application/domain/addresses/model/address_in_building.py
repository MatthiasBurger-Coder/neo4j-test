"""Domain relationship model connecting addresses and buildings."""

from dataclasses import dataclass

from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressInBuilding:
    """Represents the relationship stating that an address is in a building."""

    id: str
    address_id: str
    building_id: str
    trace_context: TraceContext | None = None
