from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.domain.entities.book import Book, Chapter


class EbookExporter(Protocol):
    """Puerto para generar los ficheros finales del manuscrito.

    Síncrono a propósito (es CPU-bound, sin I/O de red): quien lo llame
    desde código async debe hacerlo vía `asyncio.to_thread`.
    """

    def export_epub(self, book: "Book", chapters: list["Chapter"]) -> bytes: ...

    def export_pdf(self, book: "Book", chapters: list["Chapter"]) -> bytes: ...
