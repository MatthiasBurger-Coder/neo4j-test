import logging
from dataclasses import dataclass

from src.adapters.inbound.http.wsgi_application import JsonWsgiApplication
from src.infrastructure.bootstrap.application_repositories import ApplicationRepositories
from src.infrastructure.bootstrap.application_services import ApplicationServices


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Application-facing bootstrap result containing only consumable entry points."""

    repositories: ApplicationRepositories
    services: ApplicationServices
    http_api: JsonWsgiApplication
    logger: logging.Logger



