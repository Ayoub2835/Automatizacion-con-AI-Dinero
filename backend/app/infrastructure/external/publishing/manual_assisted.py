from typing import TYPE_CHECKING

from app.domain.entities.publishing import PublicationStatus, PublishingPlatform
from app.domain.ports.publishing_connector import ConnectorSubmissionResult

if TYPE_CHECKING:
    from app.domain.entities.book import Book, Chapter
    from app.domain.entities.publishing import Publication, PublishingAccount


class ManualAssistedConnector:
    """Conector base para plataformas sin API pública de autopublicación
    (ver ADR 0014). En vez de fallar, `submit` genera un paquete de
    instrucciones para que un humano complete la subida en el panel de la
    plataforma; el estado queda en SUBMITTED (enviado a revisión humana) y
    pasa a LIVE cuando el usuario lo confirma manualmente vía
    PublishingService.mark_live — nunca se inventa una publicación real.
    """

    supports_automatic_submission = False

    def __init__(
        self,
        platform: PublishingPlatform,
        required_fields: list[str],
        upload_url: str,
        notes: str,
    ) -> None:
        self.platform = platform
        self._required_fields = required_fields
        self._upload_url = upload_url
        self._notes = notes

    def required_metadata_fields(self) -> list[str]:
        return list(self._required_fields)

    async def submit(
        self,
        book: "Book",
        chapters: list["Chapter"],
        account: "PublishingAccount",
        publication: "Publication",
        epub_bytes: bytes | None,
        pdf_bytes: bytes | None,
    ) -> ConnectorSubmissionResult:
        prepared_files = []
        if epub_bytes:
            prepared_files.append("manuscrito en EPUB")
        if pdf_bytes:
            prepared_files.append("manuscrito en PDF")

        instructions = (
            f"Publicación asistida en {self.platform.value}: esta plataforma no "
            f"ofrece una API pública de autopublicación (ver notas abajo), así "
            f"que hay que completar la subida manualmente en {self._upload_url}.\n\n"
            f"1. Inicia sesión con la cuenta '{account.display_name}'.\n"
            f"2. Sube el/los fichero(s) ya preparados por BookAgent AI: "
            f"{', '.join(prepared_files) or 'ninguno generado todavía — exporta primero'}.\n"
            "3. Copia los metadatos preparados (título, subtítulo, descripción, "
            "palabras clave, categorías, precio) desde esta publicación.\n"
            "4. Cuando la plataforma confirme que el libro está publicado, "
            "vuelve aquí y márcalo como publicado indicando el identificador "
            "que te haya asignado.\n\n"
            f"Notas de la plataforma: {self._notes}"
        )
        return ConnectorSubmissionResult(
            status=PublicationStatus.SUBMITTED, instructions=instructions
        )

    async def fetch_status(
        self, account: "PublishingAccount", publication: "Publication"
    ) -> PublicationStatus | None:
        return None
