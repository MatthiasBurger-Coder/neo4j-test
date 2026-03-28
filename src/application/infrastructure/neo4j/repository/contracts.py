"""Composable contracts for building statements and projecting results."""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.application.infrastructure.neo4j.repository.result import Neo4jExecutionResult
from src.application.infrastructure.neo4j.repository.statement import CypherStatement


TRequest = TypeVar("TRequest")
TResult = TypeVar("TResult")


class CypherStatementBuilder(ABC, Generic[TRequest]):
    """Builds a structured Cypher statement from an application request model."""

    @abstractmethod
    def build(self, request_model: TRequest) -> CypherStatement:
        """Create a Cypher statement from an incoming repository request."""


class Neo4jResultProjector(ABC, Generic[TResult]):
    """Projects a plain execution result into the target repository return type."""

    @abstractmethod
    def project(self, execution_result: Neo4jExecutionResult) -> TResult:
        """Convert a plain Neo4j execution result into the adapter output model."""
