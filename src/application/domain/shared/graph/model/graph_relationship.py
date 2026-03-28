"""Shared graph relationship abstraction for the addresses domain model."""

from abc import ABC

from src.application.domain.shared.graph.model.relationship_id import RelationshipId
from src.application.infrastructure.context.trace_context import TraceContext


class GraphRelationship(ABC):
    """Minimal abstract base type for graph relationship domain models."""

    id: RelationshipId
    trace_context: TraceContext | None
