"""Structured Cypher statement models used by Neo4j repository adapters."""

from dataclasses import dataclass, field
from typing import Any, Mapping

from src.domain.shared.validation import require_non_blank_text


CypherParameters = Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class CypherStatement:
    """Represents a fully bound Cypher statement ready for execution."""

    name: str
    cypher: str
    parameters: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate statement metadata and copy input parameters defensively."""
        require_non_blank_text(owner=self.__class__.__name__, field_name="name", value=self.name)
        require_non_blank_text(owner=self.__class__.__name__, field_name="cypher", value=self.cypher)
        object.__setattr__(self, "parameters", dict(self.parameters))
        self._validate_parameter_keys()

    def _validate_parameter_keys(self) -> None:
        for key in self.parameters:
            if key.strip() == "":
                raise ValueError("CypherStatement parameter keys must not be blank")


@dataclass(frozen=True, slots=True)
class CypherStatementTemplate:
    """Provides a named and reusable Cypher template for repository statements."""

    name: str
    cypher: str

    def __post_init__(self) -> None:
        """Validate template metadata before it can be used for binding."""
        require_non_blank_text(owner=self.__class__.__name__, field_name="name", value=self.name)
        require_non_blank_text(owner=self.__class__.__name__, field_name="cypher", value=self.cypher)

    def bind(self, parameters: CypherParameters | None = None) -> CypherStatement:
        """Bind statement parameters without leaking raw Cypher strings across the codebase."""
        bound_parameters = {} if parameters is None else dict(parameters)
        return CypherStatement(name=self.name, cypher=self.cypher, parameters=bound_parameters)



