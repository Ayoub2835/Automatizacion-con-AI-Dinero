import json
from typing import Any

import anthropic

from app.domain.ports.book_content_generator import (
    ChapterOutline,
    MarketResearchResult,
    SalesCopyResult,
    TitleSuggestion,
)

_MODEL = "claude-opus-4-8"
_STRUCTURED_MAX_TOKENS = 4096
_CHAPTER_MAX_TOKENS = 8192

_WORDS_PER_PAGE = 300


class ClaudeBookContentGenerator:
    """Implementación concreta de BookContentGenerator sobre la API de Claude
    (ver ADR 0014). Cada método es una llamada independiente a Claude: las
    etapas que necesitan una forma concreta (investigación, título, esquema,
    copy comercial) usan structured outputs, igual que ClaudeDocumentClassifier
    (ADR 0011); escribir/editar capítulos y el brief de portada son texto libre.
    """

    def __init__(self, api_key: str | None) -> None:
        # Igual que ClaudeDocumentClassifier: el cliente se construye dentro
        # de cada método, no en __init__, para que la falta de API key falle
        # dentro del try/except de BookGenerationService, no al resolver la
        # dependencia FastAPI.
        self._api_key = api_key

    async def research_market(
        self, topic: str, niche: str, target_audience: str, language: str
    ) -> MarketResearchResult:
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "trending_angles": {"type": "array", "items": {"type": "string"}},
                "competitor_titles": {"type": "array", "items": {"type": "string"}},
                "recommended_keywords": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "summary",
                "trending_angles",
                "competitor_titles",
                "recommended_keywords",
            ],
            "additionalProperties": False,
        }
        prompt = (
            "Actúa como analista de mercado editorial especializado en libros "
            "de no ficción y autopublicación digital. Investiga el estado "
            f"actual del mercado para un libro sobre '{topic}' dentro del "
            f"nicho '{niche}', dirigido a '{target_audience}'. Responde en "
            f"el idioma '{language}'.\n\n"
            "Da: un resumen de tendencias (2-4 frases), 3-6 ángulos con "
            "demanda actual pero poca competencia, 3-6 títulos de libros "
            "competidores reales o plausibles en ese nicho, y 5-10 palabras "
            "clave de búsqueda relevantes para posicionar el libro."
        )
        data = await self._structured_call(prompt, schema)
        return MarketResearchResult(
            summary=data["summary"],
            trending_angles=list(data["trending_angles"]),
            competitor_titles=list(data["competitor_titles"]),
            recommended_keywords=list(data["recommended_keywords"]),
        )

    async def generate_title(
        self,
        topic: str,
        niche: str,
        target_audience: str,
        style: str,
        language: str,
        research: MarketResearchResult,
    ) -> TitleSuggestion:
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "subtitle": {"type": "string"},
            },
            "required": ["title", "subtitle"],
            "additionalProperties": False,
        }
        prompt = (
            f"Propón un título y subtítulo comerciales, en '{language}', para "
            f"un libro sobre '{topic}' (nicho: '{niche}', público objetivo: "
            f"'{target_audience}', estilo/tono: '{style}'). El título debe "
            "ser corto y memorable; el subtítulo debe aclarar el beneficio "
            "concreto para el lector y puede incorporar alguna de estas "
            f"palabras clave si encaja de forma natural: "
            f"{', '.join(research.recommended_keywords)}.\n\n"
            f"Contexto de mercado: {research.summary}"
        )
        data = await self._structured_call(prompt, schema)
        return TitleSuggestion(title=data["title"], subtitle=data["subtitle"])

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
    ) -> list[ChapterOutline]:
        target_chapters = max(3, min(20, round(target_pages / 12)))
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "chapters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "summary": {"type": "string"},
                        },
                        "required": ["title", "summary"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["chapters"],
            "additionalProperties": False,
        }
        prompt = (
            f"Diseña la estructura de capítulos, en '{language}', para el "
            f"libro titulado '{title}: {subtitle}' sobre '{topic}' (nicho: "
            f"'{niche}', público: '{target_audience}', estilo: '{style}'). "
            f"Objetivo aproximado: {target_pages} páginas repartidas en "
            f"{target_chapters} capítulos. Para cada capítulo da un título y "
            "un resumen de 2-4 frases con lo que debe cubrir, en un orden "
            "pedagógico que construya sobre lo anterior.\n\n"
            f"Ángulos con demanda a considerar: {', '.join(research.trending_angles)}."
        )
        data = await self._structured_call(prompt, schema)
        raw_chapters = data["chapters"]
        total_words = target_pages * _WORDS_PER_PAGE
        words_per_chapter = max(400, total_words // max(1, len(raw_chapters)))
        return [
            ChapterOutline(
                order=index,
                title=chapter["title"],
                summary=chapter["summary"],
                target_word_count=words_per_chapter,
            )
            for index, chapter in enumerate(raw_chapters, start=1)
        ]

    async def write_chapter(
        self, book_title: str, style: str, language: str, chapter: ChapterOutline
    ) -> str:
        prompt = (
            f"Escribe el capítulo completo '{chapter.title}' del libro "
            f"'{book_title}', en '{language}', con estilo/tono '{style}'. "
            f"Briefing del capítulo: {chapter.summary}\n\n"
            f"Extensión objetivo: ~{chapter.target_word_count} palabras. "
            "Escribe prosa lista para publicar (no un esquema ni viñetas "
            "sueltas), con subtítulos internos si ayudan a la lectura. "
            "Devuelve solo el contenido del capítulo, sin repetir el título "
            "del libro ni añadir notas meta sobre la tarea."
        )
        return await self._text_call(prompt, max_tokens=_CHAPTER_MAX_TOKENS)

    async def edit_chapter(self, content: str, language: str) -> str:
        prompt = (
            f"Revisa y pule el siguiente capítulo, escrito en '{language}': "
            "corrige gramática, ortografía y puntuación, mejora la claridad "
            "y el ritmo de lectura, y elimina redundancias — sin cambiar el "
            "significado, la estructura ni la extensión de forma sustancial. "
            "Devuelve únicamente el texto corregido, sin comentarios.\n\n"
            f"---\n{content}"
        )
        return await self._text_call(prompt, max_tokens=_CHAPTER_MAX_TOKENS)

    async def generate_sales_copy(
        self,
        title: str,
        subtitle: str,
        topic: str,
        niche: str,
        target_audience: str,
        language: str,
        chapters_summary: str,
    ) -> SalesCopyResult:
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "blurb": {"type": "string"},
                "seo_keywords": {"type": "array", "items": {"type": "string"}},
                "categories": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["blurb", "seo_keywords", "categories"],
            "additionalProperties": False,
        }
        prompt = (
            f"Escribe el material de venta, en '{language}', para el libro "
            f"'{title}: {subtitle}' sobre '{topic}' (nicho: '{niche}', "
            f"público: '{target_audience}').\n\nResumen de contenido:\n"
            f"{chapters_summary}\n\n"
            "Da: 1) una descripción comercial ('blurb') de 150-250 palabras "
            "orientada a conversión, tipo página de producto de una tienda "
            "de libros; 2) 7-10 palabras clave SEO para la ficha del libro; "
            "3) 2-3 categorías/BISAC recomendadas para clasificarlo en "
            "tiendas como Amazon KDP o Google Play Books."
        )
        data = await self._structured_call(prompt, schema)
        return SalesCopyResult(
            blurb=data["blurb"],
            seo_keywords=list(data["seo_keywords"]),
            categories=list(data["categories"]),
        )

    async def generate_cover_brief(
        self, title: str, subtitle: str, niche: str, style: str, language: str
    ) -> str:
        prompt = (
            f"Describe, en '{language}', una idea de portada para el libro "
            f"'{title}: {subtitle}' (nicho: '{niche}', estilo/tono: "
            f"'{style}'). Incluye: composición general, paleta de colores, "
            "tipografía sugerida para título/subtítulo, elementos gráficos "
            "o iconografía, y el 'mood' general. Es un brief de diseño para "
            "un diseñador o una herramienta de generación de imágenes, no "
            "una imagen en sí — máximo 150 palabras."
        )
        return await self._text_call(prompt, max_tokens=_STRUCTURED_MAX_TOKENS)

    async def _structured_call(self, prompt: str, schema: dict[str, Any]) -> dict[str, Any]:
        client = anthropic.AsyncAnthropic(api_key=self._api_key)
        response = await client.messages.create(
            model=_MODEL,
            max_tokens=_STRUCTURED_MAX_TOKENS,
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": prompt}],
        )
        text = next(block.text for block in response.content if block.type == "text")
        result: dict[str, Any] = json.loads(text)
        return result

    async def _text_call(self, prompt: str, max_tokens: int) -> str:
        client = anthropic.AsyncAnthropic(api_key=self._api_key)
        response = await client.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return next(block.text for block in response.content if block.type == "text").strip()
