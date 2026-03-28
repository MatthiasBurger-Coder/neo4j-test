"""Domain node model for city nodes."""

from dataclasses import dataclass

from src.domain.shared.graph.model.graph_node import GraphNode
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_non_blank_text, require_optional_non_blank_text


@dataclass(slots=True)
class City(GraphNode):
    """Represents a city as an independent graph node."""

    id: NodeId
    name: str
    country: str
    postal_code: str | None = None

    def __post_init__(self) -> None:
        """Validate mandatory and optional city attributes."""
        self.name = require_non_blank_text(owner=self.__class__.__name__, field_name="name", value=self.name)
        self.country = require_non_blank_text(
            owner=self.__class__.__name__,
            field_name="country",
            value=self.country,
        )
        self.postal_code = require_optional_non_blank_text(
            owner=self.__class__.__name__,
            field_name="postal_code",
            value=self.postal_code,
        )



