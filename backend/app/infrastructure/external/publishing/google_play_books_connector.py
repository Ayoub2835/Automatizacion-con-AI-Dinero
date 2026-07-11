from typing import TYPE_CHECKING

from app.domain.entities.publishing import PublishingPlatform
from app.domain.ports.publishing_connector import ConnectorSubmissionResult
from app.infrastructure.external.publishing.manual_assisted import ManualAssistedConnector

if TYPE_CHECKING:
    from app.domain.entities.book import Book, Chapter
    from app.domain.entities.publishing import Publication, PublishingAccount

_REQUIRED_FIELDS = [
    "title",
    "subtitle",
    "description",
    "keywords",
    "categories",
    "price",
]


class GooglePlayBooksConnector(ManualAssistedConnector):
    """A diferencia de KDP/Apple Books/Kobo, Google Play Books **sí** expone
    una API para socios editoriales (Partner Center / Google Books Partner
    API) capaz de crear libros y subir el fichero mediante integración
    directa. Requiere un acuerdo de partner firmado con Google y
    credenciales OAuth2 de cuenta de servicio — fuera del alcance de un
    autor individual en un MVP, así que este conector opera en modo manual
    por defecto (ver ADR 0014).

    `api_enabled` es el punto de extensión explícito: cuando la
    organización tenga esas credenciales de partner, activar
    `GOOGLE_PLAY_BOOKS_API_ENABLED=true` e implementar
    `_submit_via_partner_api` con la llamada real a la API — sin tocar
    PublishingService ni el resto del sistema.
    """

    def __init__(self, api_enabled: bool = False) -> None:
        super().__init__(
            platform=PublishingPlatform.GOOGLE_PLAY_BOOKS,
            required_fields=_REQUIRED_FIELDS,
            upload_url="https://play.google.com/books/publish",
            notes="Formatos aceptados: EPUB o PDF.",
        )
        self._api_enabled = api_enabled
        self.supports_automatic_submission = api_enabled

    async def submit(
        self,
        book: "Book",
        chapters: list["Chapter"],
        account: "PublishingAccount",
        publication: "Publication",
        epub_bytes: bytes | None,
        pdf_bytes: bytes | None,
    ) -> ConnectorSubmissionResult:
        if not self._api_enabled:
            return await super().submit(book, chapters, account, publication, epub_bytes, pdf_bytes)
        return await self._submit_via_partner_api()

    async def _submit_via_partner_api(self) -> ConnectorSubmissionResult:
        raise NotImplementedError(
            "Integración real con la API de socios de Google Play Books "
            "pendiente de implementar: requiere credenciales OAuth2 de "
            "cuenta de servicio del partner (Google Play Books Partner "
            "Center) y mapear Publication al recurso 'Book' de esa API. "
            "Desactiva GOOGLE_PLAY_BOOKS_API_ENABLED hasta implementarlo."
        )
