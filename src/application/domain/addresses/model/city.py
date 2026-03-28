"""Domain node model for city nodes."""

from dataclasses import dataclass

from src.application.domain.addresses.model.graph_node import GraphNode
from src.application.domain.addresses.model.node_id import NodeId


@dataclass(slots=True)
class City(GraphNode):
    """Represents a city as an independent graph node."""

    id: NodeId
    name: str
    country: str
    postal_code: str | None = None

    def __post_init__(self) -> None:
        """Validate mandatory and optional city attributes."""
        if self.name.strip() == "":
            raise ValueError("City name must not be blank")
        if self.country.strip() == "":
            raise ValueError("City country must not be blank")
        if self.postal_code is not None and self.postal_code.strip() == "":
            raise ValueError("City postal_code must not be blank when provided")
