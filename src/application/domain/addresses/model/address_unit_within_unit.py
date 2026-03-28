"""Domain relationship model for hierarchical address unit composition."""

from dataclasses import dataclass

from src.application.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.domain.shared.graph.model.relationship_id import RelationshipId
from src.application.infrastructure.context.trace_context import TraceContext


@dataclass(slots=True)
class AddressUnitWithinUnit(GraphRelationship):
    """Represents that one address unit is structurally within another unit."""

    id: RelationshipId
    parent_unit_id: NodeId
    child_unit_id: NodeId
    trace_context: TraceContext | None = None
