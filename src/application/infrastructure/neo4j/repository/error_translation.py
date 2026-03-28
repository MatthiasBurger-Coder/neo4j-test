"""Translates infrastructure failures into repository-specific exceptions."""

from dataclasses import dataclass
from typing import Mapping, Protocol

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.error import (
    Neo4jReadRepositoryError,
    Neo4jRepositoryError,
    Neo4jWriteRepositoryError,
)
from src.application.infrastructure.neo4j.repository.operation import Neo4jRepositoryOperationContext
from src.application.infrastructure.neo4j.repository.registry import Neo4jAccessModeRegistry


class Neo4jRepositoryErrorFactory(Protocol):
    """Strategy contract for building repository exceptions per access mode."""

    def create(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        failure_stage: str,
        technical_message: str,
    ) -> Neo4jRepositoryError:
        """Create a concrete repository error for the current access mode."""


class Neo4jReadRepositoryErrorFactory:
    """Creates read-side repository exceptions."""

    def create(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        failure_stage: str,
        technical_message: str,
    ) -> Neo4jRepositoryError:
        return Neo4jReadRepositoryError(
            message="Neo4j read repository operation failed",
            context=context,
            failure_stage=failure_stage,
            technical_message=technical_message,
        )


class Neo4jWriteRepositoryErrorFactory:
    """Creates write-side repository exceptions."""

    def create(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        failure_stage: str,
        technical_message: str,
    ) -> Neo4jRepositoryError:
        return Neo4jWriteRepositoryError(
            message="Neo4j write repository operation failed",
            context=context,
            failure_stage=failure_stage,
            technical_message=technical_message,
        )


@dataclass(frozen=True, slots=True)
class Neo4jRepositoryErrorTranslator:
    """Dispatches exception creation without leaking branching into callers."""

    factories: Neo4jAccessModeRegistry[Neo4jRepositoryErrorFactory]

    def __init__(self, factories: Mapping[Neo4jAccessMode, Neo4jRepositoryErrorFactory] | None = None) -> None:
        resolved_factories = factories or {
            Neo4jAccessMode.READ: Neo4jReadRepositoryErrorFactory(),
            Neo4jAccessMode.WRITE: Neo4jWriteRepositoryErrorFactory(),
        }
        object.__setattr__(
            self,
            "factories",
            Neo4jAccessModeRegistry(
                registry_name=self.__class__.__name__,
                entries=resolved_factories,
            ),
        )

    def translate(
        self,
        *,
        context: Neo4jRepositoryOperationContext,
        failure_stage: str,
        technical_message: str,
    ) -> Neo4jRepositoryError:
        """Build the correct repository error based on the operation access mode."""
        return self.factories.get(context.access_mode).create(
            context=context,
            failure_stage=failure_stage,
            technical_message=technical_message,
        )
