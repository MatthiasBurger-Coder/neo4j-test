"""Domain node model for structured address unit nodes."""

from dataclasses import dataclass

from src.application.domain.addresses.model.address_unit_type import AddressUnitType
from src.application.domain.shared.graph.model.graph_node import GraphNode
from src.application.domain.shared.graph.model.node_id import NodeId


@dataclass(slots=True)
class AddressUnit(GraphNode):
    """Represents a structured address addition as an independent graph node."""

    id: NodeId
    unit_type: AddressUnitType
    value: str

    def __post_init__(self) -> None:
        """Validate required address unit data."""
        if self.value.strip() == "":
            raise ValueError("AddressUnit value must not be blank")
