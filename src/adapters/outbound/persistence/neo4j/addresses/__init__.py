"""Neo4j-backed repositories for the addresses domain."""

from src.adapters.outbound.persistence.neo4j.addresses.address_read_adapter import (
    Neo4jAddressReadAdapter,
)

__all__ = ["Neo4jAddressReadAdapter"]



