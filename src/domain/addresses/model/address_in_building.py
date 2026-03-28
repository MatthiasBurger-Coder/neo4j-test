"""Domain relationship model for address-to-building links."""

from dataclasses import dataclass

from src.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId


@dataclass(slots=True)
class AddressInBuilding(GraphRelationship):
    """Represents that an address is located in a building."""

    id: RelationshipId
    address_id: NodeId
    building_id: NodeId



