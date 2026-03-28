from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelatedEntityRef:
    entity_type: str
    entity_id: str

    def __repr__(self) -> str:
        return f"RelatedEntityRef(entity_type='{self.entity_type}', entity_id='{self.entity_id}')"