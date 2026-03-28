"""Domain-owned read port for address queries."""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.domain.addresses.model.address import Address
from src.domain.shared.graph.model.node_id import NodeId


@dataclass(frozen=True, slots=True)
class AddressReadCriteria:
    """Defines domain-level filters for address read operations."""

    address_ids: tuple[NodeId, ...] = ()

    def __post_init__(self) -> None:
        """Normalize and validate address filters."""
        normalized_address_ids = tuple(self.address_ids)
        self._validate_address_ids(normalized_address_ids)
        object.__setattr__(self, "address_ids", normalized_address_ids)

    @staticmethod
    def _validate_address_ids(address_ids: tuple[NodeId, ...]) -> None:
        invalid_address_ids = tuple(
            repr(address_id)
            for address_id in address_ids
            if not isinstance(address_id, NodeId)
        )
        if invalid_address_ids:
            raise TypeError(
                "AddressReadCriteria address_ids must contain only NodeId instances: "
                + ", ".join(invalid_address_ids)
            )


class AddressReadRepositoryPort(ABC):
    """Defines the read-side contract for address retrieval."""

    @abstractmethod
    def find_by_id(self, address_id: NodeId) -> Address | None:
        """Load a single address by its domain identity."""

    @abstractmethod
    def find_all(self) -> tuple[Address, ...]:
        """Load all addresses available to the repository."""

    @abstractmethod
    def find_by_criteria(self, criteria: AddressReadCriteria) -> tuple[Address, ...]:
        """Load addresses matching the provided domain criteria."""
