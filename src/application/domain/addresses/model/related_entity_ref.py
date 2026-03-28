"""Typed references to entities outside the addresses domain."""

from dataclasses import dataclass
from enum import Enum

from src.application.domain.shared.graph.model.node_id import NodeId


class RelatedEntityType(str, Enum):
    """Defines categories of entities that can be related to an address."""

    PERSON = "PERSON"
    COMPANY = "COMPANY"
    EVENT = "EVENT"
    ORGANIZATION = "ORGANIZATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RelatedEntityRef:
    """Immutable typed reference to an external graph entity."""

    entity_type: RelatedEntityType
    entity_id: NodeId
