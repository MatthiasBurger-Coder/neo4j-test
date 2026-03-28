"""Enumeration for semantic meanings of address assignments."""

from enum import StrEnum


class AddressRelationType(StrEnum):
    """Defines business semantics of an external entity relation to an address."""

    RESIDENCE = "RESIDENCE"
    WORKPLACE = "WORKPLACE"
    REGISTERED_OFFICE = "REGISTERED_OFFICE"
    VISIT = "VISIT"
    EVENT_LOCATION = "EVENT_LOCATION"
    PRESS_LOCATION = "PRESS_LOCATION"
    MEETING_LOCATION = "MEETING_LOCATION"
    BIRTH_PLACE = "BIRTH_PLACE"
    DEATH_PLACE = "DEATH_PLACE"
    VACATION_LOCATION = "VACATION_LOCATION"
    UNKNOWN = "UNKNOWN"
