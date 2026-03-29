"""Write-side persistence models for Neo4j address-context creation."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CreateAddressNodeWriteModel:
    """Represents the write payload for an address node."""

    merge_key: str
    house_number: str
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class CreateStreetNodeWriteModel:
    """Represents the write payload for a street node."""

    merge_key: str
    name: str


@dataclass(frozen=True, slots=True)
class CreateCityNodeWriteModel:
    """Represents the write payload for a city node."""

    merge_key: str
    name: str
    country: str
    postal_code: str | None


@dataclass(frozen=True, slots=True)
class CreateBuildingNodeWriteModel:
    """Represents the write payload for a building node."""

    merge_key: str
    relationship_merge_key: str
    name: str | None
    latitude: float | None
    longitude: float | None


@dataclass(frozen=True, slots=True)
class CreateAddressUnitWriteModel:
    """Represents the write payload for one address-unit node and edge."""

    sort_index: int
    merge_key: str
    relationship_merge_key: str
    reference: str
    unit_type: str
    value: str


@dataclass(frozen=True, slots=True)
class CreateAddressUnitHierarchyWriteModel:
    """Represents the write payload for one address-unit hierarchy edge."""

    sort_index: int
    merge_key: str
    parent_unit_merge_key: str
    child_unit_merge_key: str


@dataclass(frozen=True, slots=True)
class CreateAddressAssignmentWriteModel:
    """Represents the write payload for one external-entity assignment."""

    sort_index: int
    merge_key: str
    related_entity_merge_key: str
    related_entity_type: str
    related_entity_id: str
    relation_type: str
    valid_from: str | None
    valid_to: str | None
    source: str | None
    note: str | None


@dataclass(frozen=True, slots=True)
class CreateAddressContextWriteModel:
    """Represents the full write payload for an address context."""

    address: CreateAddressNodeWriteModel
    street: CreateStreetNodeWriteModel
    city: CreateCityNodeWriteModel
    address_on_street_merge_key: str
    street_in_city_merge_key: str
    building: CreateBuildingNodeWriteModel | None = None
    units: tuple[CreateAddressUnitWriteModel, ...] = ()
    unit_hierarchy: tuple[CreateAddressUnitHierarchyWriteModel, ...] = ()
    assignments: tuple[CreateAddressAssignmentWriteModel, ...] = ()
