"""Application commands for address-context creation use cases."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoLocationCommand:
    """Carries raw geo-location input for an address-related node."""

    latitude: float
    longitude: float


@dataclass(frozen=True, slots=True)
class AddressPayloadCommand:
    """Carries raw address input."""

    house_number: str
    geo_location: GeoLocationCommand | None = None


@dataclass(frozen=True, slots=True)
class StreetPayloadCommand:
    """Carries raw street input."""

    name: str


@dataclass(frozen=True, slots=True)
class CityPayloadCommand:
    """Carries raw city input."""

    name: str
    country: str
    postal_code: str | None = None


@dataclass(frozen=True, slots=True)
class BuildingPayloadCommand:
    """Carries raw building input."""

    name: str | None = None
    geo_location: GeoLocationCommand | None = None


@dataclass(frozen=True, slots=True)
class AddressUnitPayloadCommand:
    """Carries raw address-unit input."""

    unit_type: str
    value: str


@dataclass(frozen=True, slots=True)
class AddressUnitHierarchyPayloadCommand:
    """Carries raw address-unit hierarchy input."""

    parent_ref: str
    child_ref: str


@dataclass(frozen=True, slots=True)
class RelatedEntityPayloadCommand:
    """Carries raw external-entity reference input."""

    entity_type: str
    entity_id: str


@dataclass(frozen=True, slots=True)
class AddressAssignmentPayloadCommand:
    """Carries raw address-assignment input."""

    related_entity: RelatedEntityPayloadCommand
    relation_type: str
    valid_from: str | None = None
    valid_to: str | None = None
    source: str | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class AddressCreateCommand:
    """Carries normalized external input for full address-context creation."""

    address: AddressPayloadCommand
    street: StreetPayloadCommand
    city: CityPayloadCommand
    building: BuildingPayloadCommand | None = None
    units: tuple[AddressUnitPayloadCommand, ...] = ()
    unit_hierarchy: tuple[AddressUnitHierarchyPayloadCommand, ...] = ()
    assignments: tuple[AddressAssignmentPayloadCommand, ...] = ()
