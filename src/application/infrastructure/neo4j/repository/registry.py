"""Validated registries for access-mode-dependent Neo4j infrastructure behavior."""

from dataclasses import dataclass
from typing import Generic, Mapping, TypeVar

from src.application.infrastructure.neo4j.repository.access_mode import Neo4jAccessMode
from src.application.infrastructure.neo4j.repository.error import Neo4jRepositoryConfigurationError
from src.application.infrastructure.validation import require_non_blank


TEntry = TypeVar("TEntry")


@dataclass(frozen=True, slots=True)
class Neo4jAccessModeRegistry(Generic[TEntry]):
    """Provides validated lookup of access-mode-specific strategies or values."""

    registry_name: str
    entries: Mapping[Neo4jAccessMode, TEntry]

    def __init__(self, *, registry_name: str, entries: Mapping[Neo4jAccessMode, TEntry]) -> None:
        normalized_registry_name = require_non_blank(
            owner=self.__class__.__name__,
            field_name="registry_name",
            value=registry_name,
        )
        normalized_entries = dict(entries)
        self._validate_entries(normalized_registry_name, normalized_entries)
        object.__setattr__(self, "registry_name", normalized_registry_name)
        object.__setattr__(self, "entries", normalized_entries)

    def get(self, access_mode: Neo4jAccessMode) -> TEntry:
        """Return the configured entry for the requested access mode."""
        if not isinstance(access_mode, Neo4jAccessMode):
            raise Neo4jRepositoryConfigurationError(
                f"{self.registry_name} received unsupported access mode {access_mode!r}"
            )

        try:
            return self.entries[access_mode]
        except KeyError as error:
            raise Neo4jRepositoryConfigurationError(
                f"{self.registry_name} does not define an entry for access mode '{access_mode.value}'"
            ) from error

    @staticmethod
    def _validate_entries(registry_name: str, entries: Mapping[Neo4jAccessMode, TEntry]) -> None:
        invalid_keys = tuple(repr(key) for key in entries if not isinstance(key, Neo4jAccessMode))
        if invalid_keys:
            raise Neo4jRepositoryConfigurationError(
                f"{registry_name} contains invalid access mode keys: {', '.join(invalid_keys)}"
            )

        missing_modes = tuple(mode.value for mode in Neo4jAccessMode.all() if mode not in entries)
        if missing_modes:
            raise Neo4jRepositoryConfigurationError(
                f"{registry_name} is missing entries for access modes: {', '.join(missing_modes)}"
            )

        empty_entries = tuple(mode.value for mode, entry in entries.items() if entry is None)
        if empty_entries:
            raise Neo4jRepositoryConfigurationError(
                f"{registry_name} contains empty entries for access modes: {', '.join(empty_entries)}"
            )
