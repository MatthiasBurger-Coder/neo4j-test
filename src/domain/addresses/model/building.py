"""Domain node model for building nodes."""

from dataclasses import dataclass

from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.graph_node import GraphNode
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_optional_non_blank_text


@dataclass(slots=True)
class Building(GraphNode):
    """Represents a physical building as an independent graph node."""

    id: NodeId
    name: str | None = None
    geo_location: GeoLocation | None = None

    def __post_init__(self) -> None:
        """Validate optional building attributes when present."""
        self.name = require_optional_non_blank_text(
            owner=self.__class__.__name__,
            field_name="name",
            value=self.name,
        )



