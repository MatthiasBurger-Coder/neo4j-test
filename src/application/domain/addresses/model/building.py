"""Domain node model for building nodes."""

from dataclasses import dataclass

from src.application.domain.addresses.model.geo_location import GeoLocation
from src.application.domain.addresses.model.graph_node import GraphNode
from src.application.domain.addresses.model.node_id import NodeId


@dataclass(slots=True)
class Building(GraphNode):
    """Represents a physical building as an independent graph node."""

    id: NodeId
    name: str | None = None
    geo_location: GeoLocation | None = None

    def __post_init__(self) -> None:
        """Validate optional building attributes when present."""
        if self.name is not None and self.name.strip() == "":
            raise ValueError("Building name must not be blank when provided")
