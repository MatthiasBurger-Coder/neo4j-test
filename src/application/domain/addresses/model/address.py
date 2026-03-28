"""Domain node model for neutral address nodes."""

from dataclasses import dataclass

from src.application.domain.addresses.model.geo_location import GeoLocation
from src.application.domain.addresses.model.graph_node import GraphNode
from src.application.domain.addresses.model.node_id import NodeId


@dataclass(slots=True)
class Address(GraphNode):
    """Represents a neutral addressable place without external semantics."""

    id: NodeId
    house_number: str
    geo_location: GeoLocation | None = None

    def __post_init__(self) -> None:
        """Validate required address fields."""
        if self.house_number.strip() == "":
            raise ValueError("Address house_number must not be blank")

    def has_geo_location(self) -> bool:
        """Return whether this address includes explicit coordinates."""
        return self.geo_location is not None
