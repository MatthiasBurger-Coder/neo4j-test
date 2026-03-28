from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import uuid4

from src.application.domain.addresses.model.address_relation_type import AddressRelationType
from src.application.domain.addresses.model.related_entity_ref import RelatedEntityRef


@dataclass(slots=True)
class AddressAssignment:
    related_entity: RelatedEntityRef
    address_id: str
    relation_type: AddressRelationType
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    source: Optional[str] = None
    note: Optional[str] = None
    id: str = field(default_factory=lambda: str(uuid4()))

    def is_active(self, at: Optional[datetime] = None) -> bool:
        if at is None:
            at = datetime.utcnow()

        if self.valid_from and at < self.valid_from:
            return False

        if self.valid_to and at > self.valid_to:
            return False

        return True