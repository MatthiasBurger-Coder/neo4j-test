"""Domain node model for street nodes."""

from dataclasses import dataclass

from src.application.domain.addresses.model.graph_node import GraphNode
from src.application.domain.addresses.model.node_id import NodeId


@dataclass(slots=True)
class Street(GraphNode):
    """Represents a street as an independent graph node."""

    id: NodeId
    name: str

    def __post_init__(self) -> None:
        """Validate mandatory street attributes."""
        if self.name.strip() == "":
            raise ValueError("Street name must not be blank")
