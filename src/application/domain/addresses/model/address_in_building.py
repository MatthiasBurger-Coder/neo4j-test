"""Domain relationship model for address-to-building links."""

from dataclasses import dataclass

from src.application.domain.addresses.model.node_id import NodeId
from src.application.domain.addresses.model.relationship_id import RelationshipId
from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressInBuilding:
    """Represents that an address is located in a building."""

    id: RelationshipId
    address_id: NodeId
    building_id: NodeId
    trace_context: TraceContext | None = None
