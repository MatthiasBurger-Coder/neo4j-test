"""Shared graph relationship abstraction for the addresses domain model."""

from abc import ABC

from src.application.domain.addresses.model.relationship_id import RelationshipId
from src.application.domain.addresses.model.trace_context import TraceContext


class GraphRelationship(ABC):
    """Minimal abstract base type for graph relationship domain models."""

    id: RelationshipId
    trace_context: TraceContext | None
