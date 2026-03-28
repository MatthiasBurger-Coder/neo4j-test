"""Shared graph node abstraction for the addresses domain model."""

from abc import ABC

from src.domain.shared.graph.model.node_id import NodeId


class GraphNode(ABC):
    """Minimal abstract base type for graph node domain models."""

    id: NodeId



