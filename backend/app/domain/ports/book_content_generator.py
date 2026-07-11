from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class MarketResearchResult:
    summary: str
    trending_angles: list[str]
    competitor_titles: list[str]
    recommended_keywords: list[str]


@dataclass
class TitleSuggestion:
    title: str
    subtitle: str


@dataclass
class ChapterOutline:
    order: int
    title: str
    summary: str
    target_word_count: int


@dataclass
class SalesCopyResult:
    blurb: str
    seo_keywords: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)


class BookContentGenerator(Protocol):
    """Puerto para el agente de generación de contenido (ver ADR 0014).

    Cada método cubre una etapa del pipeline autónomo; BookGenerationService
    las orquesta en orden y persiste el resultado tras cada una. No hay un
    método "generar libro completo" a propósito: así el panel puede mostrar
    progreso incremental y una etapa fallida no pierde el trabajo previo.
    """

    async def research_market(
        self, topic: str, niche: str, target_audience: str, language: str
    ) -> MarketResearchResult: ...

    async def generate_title(
        self,
        topic: str,
        niche: str,
        target_audience: str,
        style: str,
        language: str,
        research: MarketResearchResult,
    ) -> TitleSuggestion: ...

    async def generate_outline(
        self,
        title: str,
        subtitle: str,
        topic: str,
        niche: str,
        target_audience: str,
        style: str,
        language: str,
        target_pages: int,
        research: MarketResearchResult,
    ) -> list[ChapterOutline]: ...

    async def write_chapter(
        self,
        book_title: str,
        style: str,
        language: str,
        chapter: ChapterOutline,
    ) -> str:
        """Devuelve el contenido en bruto del capítulo (markdown/texto plano)."""
        ...

    async def edit_chapter(self, content: str, language: str) -> str:
        """Pasada de revisión de gramática/calidad sobre un capítulo ya escrito."""
        ...

    async def generate_sales_copy(
        self,
        title: str,
        subtitle: str,
        topic: str,
        niche: str,
        target_audience: str,
        language: str,
        chapters_summary: str,
    ) -> SalesCopyResult: ...

    async def generate_cover_brief(
        self, title: str, subtitle: str, niche: str, style: str, language: str
    ) -> str:
        """Idea de portada en texto (composición, paleta, tipografía, mood) —
        no genera la imagen; ver ADR 0014 sobre por qué queda fuera del MVP."""
        ...
