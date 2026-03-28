from enum import Enum


class AddressRelationType(str, Enum):
    RESIDENCE = "RESIDENCE"
    WORKPLACE = "WORKPLACE"
    REGISTERED_OFFICE = "REGISTERED_OFFICE"
    VISIT = "VISIT"
    EVENT_LOCATION = "EVENT_LOCATION"
    PRESS_LOCATION = "PRESS_LOCATION"
    BIRTH_PLACE = "BIRTH_PLACE"
    DEATH_PLACE = "DEATH_PLACE"
    VACATION_LOCATION = "VACATION_LOCATION"
    MEETING_LOCATION = "MEETING_LOCATION"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "AddressRelationType":
        try:
            return cls(value.upper())
        except ValueError:
            return cls.UNKNOWN