"""Internal runtime resources owned by the application bootstrap."""

from dataclasses import dataclass
from typing import Protocol


class ClosableResource(Protocol):
    """Minimal technical lifecycle contract for runtime resources."""

    def close(self) -> None:
        """Release the underlying technical resource."""


@dataclass(frozen=True, slots=True)
class ApplicationRuntime:
    """Holds internal runtime resources without exposing infrastructure types to the context."""

    resources: tuple[ClosableResource, ...]

    @classmethod
    def from_resources(cls, *resources: ClosableResource) -> "ApplicationRuntime":
        return cls(resources=tuple(resources))

    def close(self) -> None:
        for resource in reversed(self.resources):
            resource.close()
