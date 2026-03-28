"""Enumeration for semantic meaning of external address relations."""

from enum import StrEnum


class AddressRelationType(StrEnum):
    """Defines the business meaning of an external entity's relation to an address."""

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
