"""Typed external entity references for cross-domain address assignments."""

from dataclasses import dataclass
from enum import StrEnum


class RelatedEntityType(StrEnum):
    """Defines external entity categories that can relate to an address."""

    PERSON = "PERSON"
    COMPANY = "COMPANY"
    EVENT = "EVENT"
    ORGANIZATION = "ORGANIZATION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True, slots=True)
class RelatedEntityRef:
    """Immutable, typed reference to an external domain entity."""

    entity_type: RelatedEntityType
    entity_id: str
