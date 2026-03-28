"""Neo4j-backed repositories for the addresses domain."""

from src.application.infrastructure.neo4j.addresses.address_by_id_repository import Neo4jAddressByIdRepository

__all__ = ["Neo4jAddressByIdRepository"]
