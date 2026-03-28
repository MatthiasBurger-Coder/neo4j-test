"""Domain relationship model for address-to-street links."""

from dataclasses import dataclass

from src.application.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.domain.shared.graph.model.relationship_id import RelationshipId


@dataclass(slots=True)
class AddressOnStreet(GraphRelationship):
    """Represents that an address lies on a street."""

    id: RelationshipId
    address_id: NodeId
    street_id: NodeId
