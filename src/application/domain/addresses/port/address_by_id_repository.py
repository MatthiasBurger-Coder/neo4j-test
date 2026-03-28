"""Application-facing port for reading addresses by identifier."""

from abc import ABC
from dataclasses import dataclass

from src.application.domain.addresses.model.address import Address
from src.application.domain.shared.graph.model.node_id import NodeId
from src.application.port.outbound.repository.read_repository import ReadRepositoryPort


@dataclass(frozen=True, slots=True)
class FindAddressByIdQuery:
    """Query model for resolving a single address by its node identifier."""

    address_id: NodeId


class AddressByIdRepositoryPort(ReadRepositoryPort[FindAddressByIdQuery, Address | None], ABC):
    """Defines read access to address data by identifier."""
