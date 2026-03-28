"""Domain node model for neutral address nodes."""

from dataclasses import dataclass

from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.shared.graph.model.graph_node import GraphNode
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_non_blank_text


@dataclass(slots=True)
class Address(GraphNode):
    """Represents a neutral addressable place without external semantics."""

    id: NodeId
    house_number: str
    geo_location: GeoLocation | None = None

    def __post_init__(self) -> None:
        """Validate required address fields."""
        self.house_number = require_non_blank_text(
            owner=self.__class__.__name__,
            field_name="house_number",
            value=self.house_number,
        )

    def has_geo_location(self) -> bool:
        """Return whether this address includes explicit coordinates."""
        return self.geo_location is not None



