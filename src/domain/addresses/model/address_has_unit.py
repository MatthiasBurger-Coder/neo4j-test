"""Domain relationship model for address-to-unit links."""

from dataclasses import dataclass

from src.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId


@dataclass(slots=True)
class AddressHasUnit(GraphRelationship):
    """Represents that an address has a structured address unit."""

    id: RelationshipId
    address_id: NodeId
    address_unit_id: NodeId



