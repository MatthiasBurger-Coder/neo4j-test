"""Domain node model for structured address unit nodes."""

from dataclasses import dataclass

from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.shared.graph.model.graph_node import GraphNode
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.validation import require_non_blank_text


@dataclass(slots=True)
class AddressUnit(GraphNode):
    """Represents a structured address addition as an independent graph node."""

    id: NodeId
    unit_type: AddressUnitType
    value: str

    def __post_init__(self) -> None:
        """Validate required address unit data."""
        self.value = require_non_blank_text(
            owner=self.__class__.__name__,
            field_name="value",
            value=self.value,
        )



