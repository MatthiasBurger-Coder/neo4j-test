"""Domain relationship model for external entity to address assignments."""

from dataclasses import dataclass
from datetime import UTC, datetime

from src.application.domain.addresses.model.address_relation_type import AddressRelationType
from src.application.domain.addresses.model.related_entity_ref import RelatedEntityRef
from src.application.domain.addresses.model.trace_context import TraceContext


@dataclass(slots=True)
class AddressAssignment:
    """Represents semantic assignment of an external entity to an address."""

    id: str
    related_entity: RelatedEntityRef
    address_id: str
    relation_type: AddressRelationType
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source: str | None = None
    note: str | None = None
    trace_context: TraceContext | None = None

    def is_active(self, at: datetime | None = None) -> bool:
        """Return whether this assignment is active at the provided timestamp."""
        reference_time = at if at is not None else self._current_time()

        if self.valid_from is not None and reference_time < self.valid_from:
            return False
        if self.valid_to is not None and reference_time > self.valid_to:
            return False
        return True

    def _current_time(self) -> datetime:
        """Return a timezone-aware default timestamp for activity checks."""
        if self.valid_from and self.valid_from.tzinfo is not None:
            return datetime.now(self.valid_from.tzinfo)
        if self.valid_to and self.valid_to.tzinfo is not None:
            return datetime.now(self.valid_to.tzinfo)
        return datetime.now(UTC)
