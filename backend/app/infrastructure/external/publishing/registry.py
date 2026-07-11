from app.domain.entities.publishing import PublishingPlatform
from app.domain.ports.publishing_connector import PublishingConnector
from app.infrastructure.external.publishing.apple_books_connector import AppleBooksConnector
from app.infrastructure.external.publishing.google_play_books_connector import (
    GooglePlayBooksConnector,
)
from app.infrastructure.external.publishing.kdp_connector import KdpConnector
from app.infrastructure.external.publishing.kobo_connector import KoboConnector


class PublishingConnectorRegistry:
    """Resuelve el PublishingConnector concreto de cada plataforma soportada
    (ver ADR 0014). Punto único de extensión: añadir una plataforma nueva es
    registrar un conector más aquí, sin tocar PublishingService.
    """

    def __init__(self, google_play_books_api_enabled: bool = False) -> None:
        self._connectors: dict[PublishingPlatform, PublishingConnector] = {
            PublishingPlatform.KDP: KdpConnector(),
            PublishingPlatform.APPLE_BOOKS: AppleBooksConnector(),
            PublishingPlatform.GOOGLE_PLAY_BOOKS: GooglePlayBooksConnector(
                api_enabled=google_play_books_api_enabled
            ),
            PublishingPlatform.KOBO: KoboConnector(),
        }

    def get(self, platform: PublishingPlatform) -> PublishingConnector:
        return self._connectors[platform]
