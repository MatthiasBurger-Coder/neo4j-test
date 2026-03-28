"""Cypher query definitions for address read operations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Mapping

from src.adapters.outbound.persistence.neo4j.repository.contracts import CypherStatementBuilder
from src.adapters.outbound.persistence.neo4j.repository.statement import CypherStatement
from src.domain.addresses.ports.address_read_repository import AddressReadCriteria


@dataclass(frozen=True, slots=True)
class AddressCriteriaClause:
    """Represents a reusable Cypher predicate with its parameters."""

    predicate: str
    parameters: Mapping[str, object]


class AddressCriteriaClauseStrategy(ABC):
    """Builds an optional Cypher predicate from address criteria."""

    @abstractmethod
    def build(self, criteria: AddressReadCriteria) -> AddressCriteriaClause | None:
        """Return a predicate clause for the provided criteria."""


class AddressIdsClauseStrategy(AddressCriteriaClauseStrategy):
    """Builds the identifier filter clause when criteria include address ids."""

    def build(self, criteria: AddressReadCriteria) -> AddressCriteriaClause | None:
        return _ADDRESS_IDS_CLAUSE_BUILDERS[bool(criteria.address_ids)](criteria)


class FindAddressesByCriteriaStatementBuilder(CypherStatementBuilder[AddressReadCriteria]):
    """Builds the read-side address query from reusable criteria clause strategies."""

    def __init__(
        self,
        clause_strategies: tuple[AddressCriteriaClauseStrategy, ...] | None = None,
    ) -> None:
        self._clause_strategies = clause_strategies or (AddressIdsClauseStrategy(),)

    def build(self, request_model: AddressReadCriteria) -> CypherStatement:
        clauses = tuple(
            clause
            for clause in (
                strategy.build(request_model)
                for strategy in self._clause_strategies
            )
            if clause is not None
        )
        return CypherStatement(
            name="address.find_by_criteria",
            cypher=_ADDRESS_READ_QUERY_TEMPLATE.format(
                where_clause=_WHERE_CLAUSE_RENDERERS[bool(clauses)](clauses)
            ).strip(),
            parameters=_merge_clause_parameters(clauses),
        )


def _build_without_address_ids(criteria: AddressReadCriteria) -> AddressCriteriaClause | None:
    del criteria
    return None


def _build_with_address_ids(criteria: AddressReadCriteria) -> AddressCriteriaClause:
    return AddressCriteriaClause(
        predicate="address.id IN $address_ids",
        parameters={"address_ids": tuple(str(address_id) for address_id in criteria.address_ids)},
    )


def _render_query_without_where(clauses: tuple[AddressCriteriaClause, ...]) -> str:
    del clauses
    return ""


def _render_query_with_where(clauses: tuple[AddressCriteriaClause, ...]) -> str:
    return "WHERE " + " AND ".join(clause.predicate for clause in clauses)


def _merge_clause_parameters(clauses: tuple[AddressCriteriaClause, ...]) -> dict[str, object]:
    merged_parameters: dict[str, object] = {}
    for clause in clauses:
        merged_parameters.update(clause.parameters)
    return merged_parameters


_ADDRESS_IDS_CLAUSE_BUILDERS = {
    False: _build_without_address_ids,
    True: _build_with_address_ids,
}

_WHERE_CLAUSE_RENDERERS = {
    False: _render_query_without_where,
    True: _render_query_with_where,
}

_ADDRESS_READ_QUERY_TEMPLATE = """
MATCH (address:Address)
{where_clause}
RETURN
    address.id AS address_id,
    address.house_number AS house_number,
    address.latitude AS latitude,
    address.longitude AS longitude
ORDER BY address.id
"""
