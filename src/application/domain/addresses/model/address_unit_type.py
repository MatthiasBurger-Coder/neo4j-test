"""Enumeration for structured address unit categories."""

from enum import StrEnum


class AddressUnitType(StrEnum):
    """Defines standardized structured address unit categories."""

    BUILDING_SECTION = "BUILDING_SECTION"
    ENTRANCE = "ENTRANCE"
    STAIRCASE = "STAIRCASE"
    FLOOR = "FLOOR"
    APARTMENT = "APARTMENT"
    ROOM = "ROOM"
    UNIT = "UNIT"
    UNKNOWN = "UNKNOWN"
