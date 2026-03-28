"""Domain relationship model for semantic external-entity address assignments."""

from dataclasses import dataclass
from datetime import datetime, timezone

from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef
from src.domain.shared.graph.model.graph_relationship import GraphRelationship
from src.domain.shared.graph.model.node_id import NodeId
from src.domain.shared.graph.model.relationship_id import RelationshipId
from src.domain.shared.validation import require_optional_non_blank_text


@dataclass(slots=True)
class AddressAssignment(GraphRelationship):
    """Represents that an external entity has a semantic relation to an address."""

    id: RelationshipId
    related_entity: RelatedEntityRef
    address_id: NodeId
    relation_type: AddressRelationType
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source: str | None = None
    note: str | None = None

    def __post_init__(self) -> None:
        """Validate temporal and textual assignment invariants."""
        if self.valid_from is not None and self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("AddressAssignment valid_to must not be earlier than valid_from")
        self.source = require_optional_non_blank_text(
            owner=self.__class__.__name__,
            field_name="source",
            value=self.source,
        )
        self.note = require_optional_non_blank_text(
            owner=self.__class__.__name__,
            field_name="note",
            value=self.note,
        )

    def is_active(self, at: datetime | None = None) -> bool:
        """Return whether the assignment is active at the given moment."""
        reference_time = at if at is not None else self._default_reference_time()

        if self.valid_from is not None and reference_time < self.valid_from:
            return False
        if self.valid_to is not None and reference_time > self.valid_to:
            return False
        return True

    def _default_reference_time(self) -> datetime:
        """Determine a default reference time matching assignment timezone semantics."""
        if self.valid_from is not None:
            return datetime.now(self.valid_from.tzinfo)
        if self.valid_to is not None:
            return datetime.now(self.valid_to.tzinfo)
        return datetime.now(timezone.utc)



