"""Domain node model for street nodes."""

from dataclasses import dataclass

from src.domain.shared.graph.model.graph_node import GraphNode
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_non_blank_text


@dataclass(slots=True)
class Street(GraphNode):
    """Represents a street as an independent graph node."""

    id: NodeId
    name: str

    def __post_init__(self) -> None:
        """Validate mandatory street attributes."""
        self.name = require_non_blank_text(owner=self.__class__.__name__, field_name="name", value=self.name)



