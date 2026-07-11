import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.domain.entities.book import Book, BookStatus, Chapter, ChapterStatus, GenerationStage
from app.domain.ports.book_content_generator import (
    BookContentGenerator,
    ChapterOutline,
    MarketResearchResult,
    TitleSuggestion,
)
from app.domain.repositories.book_repository import BookRepository
from app.domain.repositories.chapter_repository import ChapterRepository

logger = logging.getLogger(__name__)

_Commit = Callable[[], Awaitable[None]]


async def _noop_commit() -> None:
    return None


class BookGenerationService:
    """El agente autónomo de generación de contenido (ver ADR 0014): orquesta
    investigación de mercado, título, esquema, redacción, edición y copy
    comercial de un libro, en ese orden.

    Cada etapa se persiste (y se confirma vía `on_stage_committed`, ver
    abajo) al terminar, así que un fallo a mitad de pipeline no pierde el
    trabajo previo y el panel puede mostrar progreso incremental leyendo
    `Book.generation_stage` mientras el pipeline sigue corriendo en segundo
    plano — ver `run_generation_pipeline` en `app/api/v1/routers/books.py`
    para cómo se lanza como BackgroundTask.

    `on_stage_committed` es un callback opcional (normalmente `session.commit`)
    que se llama tras persistir cada checkpoint. Este servicio no importa
    SQLAlchemy directamente (regla de dependencia hexagonal) pero sí necesita
    forzar commits intermedios — algo que un caso de uso disparado por un
    router normal no necesita porque el router hace un único commit al final.
    """

    def __init__(
        self,
        books: BookRepository,
        chapters: ChapterRepository,
        generator: BookContentGenerator,
    ) -> None:
        self._books = books
        self._chapters = chapters
        self._generator = generator

    async def run_pipeline(self, book: Book, on_stage_committed: _Commit | None = None) -> Book:
        commit = on_stage_committed or _noop_commit
        book.status = BookStatus.GENERATING
        book.error_message = None

        try:
            book, research = await self._run_research(book, commit)
            book, title = await self._run_title(book, research, commit)
            chapters, outline = await self._run_outline(book, title, research, commit)
            chapters = await self._run_write_chapters(book, title, chapters, outline, commit)
            chapters = await self._run_edit_chapters(book, chapters, commit)
            book = await self._run_sales_copy(book, title, chapters, commit)
            book = await self._run_cover_brief(book, title, commit)

            book.status = BookStatus.READY
            book.generation_stage = GenerationStage.DONE
            book = await self._books.update(book)
            await commit()
        except Exception as exc:
            logger.exception("book_generation_failed", extra={"book_id": str(book.id)})
            book.status = BookStatus.FAILED
            book.error_message = str(exc)
            book = await self._books.update(book)
            await commit()

        return book

    async def _run_research(self, book: Book, commit: _Commit) -> tuple[Book, MarketResearchResult]:
        book.generation_stage = GenerationStage.RESEARCH
        book = await self._books.update(book)
        await commit()

        research = await self._generator.research_market(
            book.topic, book.niche, book.target_audience, book.language
        )
        book.market_research = {
            "summary": research.summary,
            "trending_angles": research.trending_angles,
            "competitor_titles": research.competitor_titles,
            "recommended_keywords": research.recommended_keywords,
        }
        book = await self._books.update(book)
        await commit()
        return book, research

    async def _run_title(
        self, book: Book, research: MarketResearchResult, commit: _Commit
    ) -> tuple[Book, TitleSuggestion]:
        book.generation_stage = GenerationStage.TITLE
        book = await self._books.update(book)
        await commit()

        title = await self._generator.generate_title(
            book.topic, book.niche, book.target_audience, book.style, book.language, research
        )
        book.title = title.title
        book.subtitle = title.subtitle
        book = await self._books.update(book)
        await commit()
        return book, title

    async def _run_outline(
        self,
        book: Book,
        title: TitleSuggestion,
        research: MarketResearchResult,
        commit: _Commit,
    ) -> tuple[list[Chapter], list[ChapterOutline]]:
        book.generation_stage = GenerationStage.OUTLINE
        book = await self._books.update(book)
        await commit()

        outline = await self._generator.generate_outline(
            title.title,
            title.subtitle,
            book.topic,
            book.niche,
            book.target_audience,
            book.style,
            book.language,
            book.target_pages,
            research,
        )
        now = datetime.now(UTC)
        chapter_entities = [
            Chapter(
                id=uuid4(),
                book_id=book.id,
                order=item.order,
                title=item.title,
                summary=item.summary,
                created_at=now,
                updated_at=now,
            )
            for item in outline
        ]
        chapters = await self._chapters.replace_outline(book.id, chapter_entities)
        await commit()
        return chapters, outline

    async def _run_write_chapters(
        self,
        book: Book,
        title: TitleSuggestion,
        chapters: list[Chapter],
        outline: list[ChapterOutline],
        commit: _Commit,
    ) -> list[Chapter]:
        book.generation_stage = GenerationStage.CHAPTERS
        book = await self._books.update(book)
        await commit()

        outline_by_order = {item.order: item for item in outline}
        for chapter in chapters:
            content = await self._generator.write_chapter(
                title.title, book.style, book.language, outline_by_order[chapter.order]
            )
            chapter.content = content
            chapter.word_count = len(content.split())
            chapter.status = ChapterStatus.DRAFTED
            await self._chapters.update(chapter)
            await commit()
        return chapters

    async def _run_edit_chapters(
        self, book: Book, chapters: list[Chapter], commit: _Commit
    ) -> list[Chapter]:
        book.generation_stage = GenerationStage.EDITING
        book = await self._books.update(book)
        await commit()

        for chapter in chapters:
            edited = await self._generator.edit_chapter(chapter.content or "", book.language)
            chapter.content = edited
            chapter.word_count = len(edited.split())
            chapter.status = ChapterStatus.EDITED
            await self._chapters.update(chapter)
            await commit()
        return chapters

    async def _run_sales_copy(
        self, book: Book, title: TitleSuggestion, chapters: list[Chapter], commit: _Commit
    ) -> Book:
        book.generation_stage = GenerationStage.SALES_COPY
        book = await self._books.update(book)
        await commit()

        chapters_summary = "\n".join(f"- {c.title}: {c.summary}" for c in chapters)
        sales_copy = await self._generator.generate_sales_copy(
            title.title,
            title.subtitle,
            book.topic,
            book.niche,
            book.target_audience,
            book.language,
            chapters_summary,
        )
        book.sales_blurb = sales_copy.blurb
        book.seo_keywords = sales_copy.seo_keywords
        book.categories = sales_copy.categories
        book = await self._books.update(book)
        await commit()
        return book

    async def _run_cover_brief(self, book: Book, title: TitleSuggestion, commit: _Commit) -> Book:
        book.generation_stage = GenerationStage.COVER_BRIEF
        book = await self._books.update(book)
        await commit()

        book.cover_brief = await self._generator.generate_cover_brief(
            title.title, title.subtitle, book.niche, book.style, book.language
        )
        book = await self._books.update(book)
        await commit()
        return book
