"""Application models for validated address-context write requests and results."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.addresses.model.address import Address
from src.domain.addresses.model.address_assignment import AddressAssignment
from src.domain.addresses.model.address_has_unit import AddressHasUnit
from src.domain.addresses.model.address_in_building import AddressInBuilding
from src.domain.addresses.model.address_on_street import AddressOnStreet
from src.domain.addresses.model.address_relation_type import AddressRelationType
from src.domain.addresses.model.address_unit import AddressUnit
from src.domain.addresses.model.address_unit_type import AddressUnitType
from src.domain.addresses.model.address_unit_within_unit import AddressUnitWithinUnit
from src.domain.addresses.model.building import Building
from src.domain.addresses.model.city import City
from src.domain.addresses.model.geo_location import GeoLocation
from src.domain.addresses.model.related_entity_ref import RelatedEntityRef
from src.domain.addresses.model.street import Street
from src.domain.addresses.model.street_in_city import StreetInCity


@dataclass(frozen=True, slots=True)
class AddressContextAddressDraft:
    """Validated draft of the address node input."""

    house_number: str
    geo_location: GeoLocation | None = None


@dataclass(frozen=True, slots=True)
class AddressContextStreetDraft:
    """Validated draft of the street node input."""

    name: str


@dataclass(frozen=True, slots=True)
class AddressContextCityDraft:
    """Validated draft of the city node input."""

    name: str
    country: str
    postal_code: str | None = None


@dataclass(frozen=True, slots=True)
class AddressContextBuildingDraft:
    """Validated draft of the building node input."""

    name: str | None = None
    geo_location: GeoLocation | None = None


@dataclass(frozen=True, slots=True)
class AddressContextUnitDraft:
    """Validated draft of an address unit."""

    unit_type: AddressUnitType
    value: str
    reference: str


@dataclass(frozen=True, slots=True)
class AddressContextUnitHierarchyDraft:
    """Validated draft of one unit-hierarchy edge."""

    parent_ref: str
    child_ref: str


@dataclass(frozen=True, slots=True)
class AddressContextAssignmentDraft:
    """Validated draft of one external-entity assignment."""

    related_entity: RelatedEntityRef
    relation_type: AddressRelationType
    valid_from: datetime | None = None
    valid_to: datetime | None = None
    source: str | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class AddressContextDraft:
    """Validated full address context handed to the write port."""

    address: AddressContextAddressDraft
    street: AddressContextStreetDraft
    city: AddressContextCityDraft
    building: AddressContextBuildingDraft | None = None
    units: tuple[AddressContextUnitDraft, ...] = ()
    unit_hierarchy: tuple[AddressContextUnitHierarchyDraft, ...] = ()
    assignments: tuple[AddressContextAssignmentDraft, ...] = ()


@dataclass(frozen=True, slots=True)
class CreatedAddressContext:
    """Represents the persisted address context returned by the write port."""

    address: Address
    street: Street
    city: City
    address_on_street: AddressOnStreet
    street_in_city: StreetInCity
    building: Building | None = None
    address_in_building: AddressInBuilding | None = None
    units: tuple[AddressUnit, ...] = ()
    address_has_units: tuple[AddressHasUnit, ...] = ()
    unit_hierarchy: tuple[AddressUnitWithinUnit, ...] = ()
    assignments: tuple[AddressAssignment, ...] = ()
