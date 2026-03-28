"""Domain relationship model for address-to-unit links."""

from dataclasses import dataclass

from src.application.domain.addresses.model.node_id import NodeId
from src.application.domain.addresses.model.relationship_id import RelationshipId
from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressHasUnit:
    """Represents that an address has a structured address unit."""

    id: RelationshipId
    address_id: NodeId
    address_unit_id: NodeId
    trace_context: TraceContext | None = None
