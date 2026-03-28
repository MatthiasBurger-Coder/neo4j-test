from dataclasses import dataclass
import logging

from src.bootstrap.application_repositories import ApplicationRepositories


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    repositories: ApplicationRepositories
    logger: logging.Logger
