"""Enumeration for structured address unit types."""

from enum import StrEnum


class AddressUnitType(StrEnum):
    """Defines standardized types for address units."""

    BUILDING_SECTION = "BUILDING_SECTION"
    ENTRANCE = "ENTRANCE"
    STAIRCASE = "STAIRCASE"
    FLOOR = "FLOOR"
    APARTMENT = "APARTMENT"
    ROOM = "ROOM"
    UNIT = "UNIT"
    UNKNOWN = "UNKNOWN"
