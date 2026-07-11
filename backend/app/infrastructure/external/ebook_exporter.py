import io
from typing import TYPE_CHECKING, Any

from ebooklib import epub
from fpdf import FPDF

if TYPE_CHECKING:
    from app.domain.entities.book import Book, Chapter


class EbookLibExporter:
    """Implementación concreta de EbookExporter con ebooklib (EPUB) y fpdf2
    (PDF) — ambas librerías puras en Python, sin dependencias de sistema
    (a diferencia de ej. WeasyPrint/Cairo), lo que simplifica el despliegue
    del MVP (ver ADR 0014).

    Limitación conocida: el PDF usa las fuentes core de fpdf2 (Helvetica),
    que solo cubren Latin-1 — títulos/capítulos en idiomas con otro alfabeto
    (ej. chino, árabe, ruso) pierden los caracteres no representables en el
    PDF (no en el EPUB, que es HTML/UTF-8 sin esa limitación). Solucionarlo
    requiere empaquetar una fuente TTF con soporte Unicode; se deja fuera
    del MVP hasta que haya demanda real de esos idiomas.
    """

    def export_epub(self, book: "Book", chapters: list["Chapter"]) -> bytes:
        epub_book = epub.EpubBook()
        epub_book.set_identifier(str(book.id))
        epub_book.set_title(book.title or book.topic)
        epub_book.set_language(book.language)

        toc: list[Any] = []
        spine: list[Any] = ["nav"]

        if book.subtitle or book.sales_blurb:
            intro = epub.EpubHtml(title="Sinopsis", file_name="intro.xhtml", lang=book.language)
            intro.content = (
                f"<h1>{_escape(book.title or book.topic)}</h1>"
                f"<h2>{_escape(book.subtitle or '')}</h2>"
                f"<p>{_paragraphs(book.sales_blurb or '')}</p>"
            )
            epub_book.add_item(intro)
            toc.append(intro)
            spine.append(intro)

        for chapter in chapters:
            item = epub.EpubHtml(
                title=chapter.title,
                file_name=f"chapter_{chapter.order:02d}.xhtml",
                lang=book.language,
            )
            item.content = (
                f"<h1>{_escape(chapter.title)}</h1><p>{_paragraphs(chapter.content or '')}</p>"
            )
            epub_book.add_item(item)
            toc.append(item)
            spine.append(item)

        epub_book.toc = toc
        epub_book.add_item(epub.EpubNcx())
        epub_book.add_item(epub.EpubNav())
        epub_book.spine = spine

        buffer = io.BytesIO()
        epub.write_epub(buffer, epub_book)
        return buffer.getvalue()

    def export_pdf(self, book: "Book", chapters: list["Chapter"]) -> bytes:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)

        pdf.add_page()
        pdf.set_font("Helvetica", "B", 24)
        _multi_cell_block(pdf, 12, _pdf_safe(book.title or book.topic))
        if book.subtitle:
            pdf.set_font("Helvetica", "", 14)
            _multi_cell_block(pdf, 10, _pdf_safe(book.subtitle))

        for chapter in chapters:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 18)
            _multi_cell_block(pdf, 10, _pdf_safe(chapter.title))
            pdf.ln(4)
            pdf.set_font("Helvetica", "", 11)
            _multi_cell_block(pdf, 7, _pdf_safe(chapter.content or ""))

        return bytes(pdf.output())


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _paragraphs(content: str) -> str:
    blocks = [_escape(block) for block in content.split("\n\n") if block.strip()]
    return "</p><p>".join(blocks)


def _pdf_safe(text: str) -> str:
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _multi_cell_block(pdf: FPDF, line_height: float, text: str) -> None:
    # fpdf2's multi_cell deja el cursor a la derecha del bloque por defecto
    # (new_x=XPos.RIGHT): sin resetearlo explícitamente a LMARGIN/NEXT, el
    # siguiente multi_cell hereda un ancho disponible mucho menor y puede
    # fallar con "Not enough horizontal space to render a single character".
    pdf.multi_cell(0, line_height, text, new_x="LMARGIN", new_y="NEXT")
