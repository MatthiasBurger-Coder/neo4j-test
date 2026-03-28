"""Domain relationship model for address-to-street links."""

from dataclasses import dataclass

from src.application.domain.addresses.model.node_id import NodeId
from src.application.domain.addresses.model.relationship_id import RelationshipId
from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressOnStreet:
    """Represents that an address lies on a street."""

    id: RelationshipId
    address_id: NodeId
    street_id: NodeId
    trace_context: TraceContext | None = None
