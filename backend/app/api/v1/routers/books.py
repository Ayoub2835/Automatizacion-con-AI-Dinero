import logging
import re
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import get_current_user, get_db_session, get_ebook_exporter
from app.api.v1.schemas.books import BookResponse, ChapterResponse, CreateBookRequest
from app.application.services.book_generation_service import BookGenerationService
from app.application.services.book_service import BookService
from app.application.services.export_service import ExportService
from app.core.config import get_settings
from app.domain.entities.book import Book, BookStatus, Chapter
from app.domain.entities.user import User
from app.domain.exceptions import InvalidStateTransitionError
from app.domain.ports.ebook_exporter import EbookExporter
from app.infrastructure.database.repositories.book_repository import SqlAlchemyBookRepository
from app.infrastructure.database.repositories.chapter_repository import (
    SqlAlchemyChapterRepository,
)
from app.infrastructure.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = APIRouter()

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def _get_book_service(session: AsyncSession = Depends(get_db_session)) -> BookService:
    return BookService(
        books=SqlAlchemyBookRepository(session), chapters=SqlAlchemyChapterRepository(session)
    )


def _get_export_service(
    session: AsyncSession = Depends(get_db_session),
    exporter: EbookExporter = Depends(get_ebook_exporter),
) -> ExportService:
    return ExportService(
        books=SqlAlchemyBookRepository(session),
        chapters=SqlAlchemyChapterRepository(session),
        exporter=exporter,
        uploads_dir=get_settings().uploads_dir,
    )


@router.post("", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    payload: CreateBookRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    book_service: BookService = Depends(_get_book_service),
) -> BookResponse:
    """Crea el libro y lanza el pipeline autónomo (investigación → título →
    esquema → capítulos → edición → copy comercial → exportación) en segundo
    plano — ver `run_generation_pipeline` más abajo y ADR 0014."""
    book = await book_service.create(
        organization_id=current_user.organization_id,
        topic=payload.topic,
        niche=payload.niche,
        target_audience=payload.target_audience,
        language=payload.language,
        style=payload.style,
        target_pages=payload.target_pages,
    )
    await session.commit()
    background_tasks.add_task(run_generation_pipeline, book.id, current_user.organization_id)
    return _to_response(book)


@router.get("", response_model=list[BookResponse])
async def list_books(
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(_get_book_service),
) -> list[BookResponse]:
    books = await book_service.list_for_organization(current_user.organization_id)
    return [_to_response(b) for b in books]


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(_get_book_service),
) -> BookResponse:
    book = await book_service.get(book_id, current_user.organization_id)
    return _to_response(book)


@router.get("/{book_id}/chapters", response_model=list[ChapterResponse])
async def list_chapters(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(_get_book_service),
) -> list[ChapterResponse]:
    chapters = await book_service.get_chapters(book_id, current_user.organization_id)
    return [_chapter_to_response(c) for c in chapters]


@router.post("/{book_id}/generate", response_model=BookResponse)
async def trigger_generation(
    book_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(_get_book_service),
) -> BookResponse:
    """Reintenta el pipeline de un libro en DRAFT (nunca se lanzó) o FAILED
    (falló a mitad, ver Book.error_message)."""
    book = await book_service.get(book_id, current_user.organization_id)
    if book.status not in (BookStatus.DRAFT, BookStatus.FAILED):
        raise InvalidStateTransitionError(
            entity="el libro", from_state=book.status.value, action="generar"
        )
    background_tasks.add_task(run_generation_pipeline, book.id, current_user.organization_id)
    return _to_response(book)


@router.post("/{book_id}/export", response_model=BookResponse)
async def export_book(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    book_service: BookService = Depends(_get_book_service),
    export_service: ExportService = Depends(_get_export_service),
) -> BookResponse:
    book = await book_service.get(book_id, current_user.organization_id)
    book = await export_service.export_book(book)
    await session.commit()
    return _to_response(book)


@router.get("/{book_id}/export/{file_format}")
async def download_export(
    book_id: UUID,
    file_format: str,
    current_user: User = Depends(get_current_user),
    book_service: BookService = Depends(_get_book_service),
) -> FileResponse:
    book = await book_service.get(book_id, current_user.organization_id)

    if file_format == "epub":
        storage_path, media_type = book.epub_storage_path, "application/epub+zip"
    elif file_format == "pdf":
        storage_path, media_type = book.pdf_storage_path, "application/pdf"
    else:
        raise HTTPException(status_code=404, detail="Formato no soportado")

    if storage_path is None:
        raise HTTPException(status_code=404, detail="Fichero no generado todavía")

    full_path = Path(get_settings().uploads_dir) / "books" / storage_path
    safe_name = _UNSAFE_FILENAME_CHARS.sub("_", book.title or book.topic).strip("._") or "libro"
    return FileResponse(full_path, media_type=media_type, filename=f"{safe_name}.{file_format}")


async def run_generation_pipeline(book_id: UUID, organization_id: UUID) -> None:
    """Ejecutado como BackgroundTask tras crear o reintentar un libro: la
    sesión del request original ya se cerró cuando esto corre, así que abre
    su propia sesión y confirma tras cada etapa (ver
    BookGenerationService.run_pipeline) para que el panel muestre progreso
    en tiempo real mientras el pipeline sigue corriendo (ver ADR 0014).

    Al terminar con éxito, encadena la exportación a EPUB/PDF — la spec
    pide "preparar archivos EPUB y PDF" como parte del flujo estándar, no
    como un paso manual aparte.

    Construye sus dependencias externas llamando a `app.api.deps` en vez
    de recibirlas por FastAPI `Depends` (BackgroundTasks corre fuera del
    ciclo de vida del request, sin inyección de dependencias) — los tests
    las sustituyen con `monkeypatch.setattr(deps, "get_book_content_generator", ...)`.
    """
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        books = SqlAlchemyBookRepository(session)
        chapters = SqlAlchemyChapterRepository(session)

        book = await books.get_by_id(book_id, organization_id)
        if book is None:
            logger.error("book_not_found_for_generation", extra={"book_id": str(book_id)})
            return

        generation_service = BookGenerationService(
            books, chapters, deps.get_book_content_generator()
        )
        book = await generation_service.run_pipeline(book, on_stage_committed=session.commit)

        if book.status != BookStatus.READY:
            return

        exporter: EbookExporter = deps.get_ebook_exporter()
        export_service = ExportService(books, chapters, exporter, settings.uploads_dir)
        try:
            await export_service.export_book(book)
            await session.commit()
        except Exception:
            logger.exception("book_export_failed", extra={"book_id": str(book_id)})


def _to_response(book: Book) -> BookResponse:
    return BookResponse(
        id=book.id,
        organization_id=book.organization_id,
        topic=book.topic,
        niche=book.niche,
        target_audience=book.target_audience,
        language=book.language,
        style=book.style,
        target_pages=book.target_pages,
        status=book.status.value,
        generation_stage=book.generation_stage.value if book.generation_stage else None,
        error_message=book.error_message,
        title=book.title,
        subtitle=book.subtitle,
        market_research=book.market_research,
        sales_blurb=book.sales_blurb,
        seo_keywords=book.seo_keywords,
        categories=book.categories,
        cover_brief=book.cover_brief,
        has_epub=book.epub_storage_path is not None,
        has_pdf=book.pdf_storage_path is not None,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


def _chapter_to_response(chapter: Chapter) -> ChapterResponse:
    return ChapterResponse(
        id=chapter.id,
        book_id=chapter.book_id,
        order=chapter.order,
        title=chapter.title,
        summary=chapter.summary,
        content=chapter.content,
        word_count=chapter.word_count,
        status=chapter.status.value,
        created_at=chapter.created_at,
        updated_at=chapter.updated_at,
    )
