"""Domain relationship model for street-to-city links."""

from dataclasses import dataclass

from src.application.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.domain.shared.graph.model.relationship_id import RelationshipId
from src.application.infrastructure.context.trace_context import TraceContext


@dataclass(slots=True)
class StreetInCity(GraphRelationship):
    """Represents that a street exists in a city."""

    id: RelationshipId
    street_id: NodeId
    city_id: NodeId
    trace_context: TraceContext | None = None
