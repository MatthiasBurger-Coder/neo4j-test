import logging
from dataclasses import dataclass

from src.infrastructure.bootstrap.application_repositories import ApplicationRepositories


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Application-facing bootstrap result containing only consumable entry points."""

    repositories: ApplicationRepositories
    logger: logging.Logger



