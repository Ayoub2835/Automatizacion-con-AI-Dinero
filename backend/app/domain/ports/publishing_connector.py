from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from app.domain.entities.publishing import PublicationStatus, PublishingPlatform

if TYPE_CHECKING:
    from app.domain.entities.book import Book, Chapter
    from app.domain.entities.publishing import Publication, PublishingAccount


@dataclass
class ConnectorSubmissionResult:
    """Resultado de intentar enviar una Publication a una plataforma.

    `status` es siempre SUBMITTED o FAILED: la transición a LIVE requiere
    confirmación explícita (automática si el conector soporta sync, manual
    en caso contrario) — ver PublishingService.mark_live.
    """

    status: PublicationStatus
    instructions: str | None = None
    external_book_id: str | None = None
    error_message: str | None = None


class PublishingConnector(Protocol):
    """Puerto para publicar un libro en una plataforma de venta concreta.

    `supports_automatic_submission=False` es el caso normal en este MVP
    (ver ADR 0014): ninguna de las plataformas soportadas ofrece hoy una
    API pública de autoservicio para autopublicación. Esos conectores
    devuelven un paquete de instrucciones para que un humano complete la
    subida, en vez de fallar — es el "proceso asistido" que pide la spec.
    """

    platform: PublishingPlatform
    supports_automatic_submission: bool

    def required_metadata_fields(self) -> list[str]:
        """Claves que `Publication.metadata` debe tener para poder enviarse."""
        ...

    async def submit(
        self,
        book: "Book",
        chapters: list["Chapter"],
        account: "PublishingAccount",
        publication: "Publication",
        epub_bytes: bytes | None,
        pdf_bytes: bytes | None,
    ) -> ConnectorSubmissionResult: ...

    async def fetch_status(
        self, account: "PublishingAccount", publication: "Publication"
    ) -> PublicationStatus | None:
        """Sincroniza el estado real desde la plataforma. Devuelve None si el
        conector no soporta sync (todos los conectores manuales de este MVP)."""
        ...
