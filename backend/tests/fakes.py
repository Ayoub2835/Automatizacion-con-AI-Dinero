from dataclasses import dataclass

from app.domain.ports.book_content_generator import (
    ChapterOutline,
    MarketResearchResult,
    SalesCopyResult,
    TitleSuggestion,
)
from app.domain.ports.document_classifier import ClassificationResult


@dataclass
class SentEmail:
    to: str
    subject: str
    body: str


class FakeEmailSender:
    """Doble de prueba de EmailSender: registra los emails en memoria en vez
    de enviarlos, para que los tests de integración no dependan de un SMTP
    real. SmtpEmailSender en sí se prueba aparte contra un servidor SMTP
    real (ver test_smtp_email_sender.py)."""

    def __init__(self) -> None:
        self.sent: list[SentEmail] = []

    async def send(self, to: str, subject: str, body: str) -> None:
        self.sent.append(SentEmail(to=to, subject=subject, body=body))


@dataclass
class RecordedClassification:
    content_type: str
    allowed_type_names: list[str]


class FakeDocumentClassifier:
    """Doble de prueba de DocumentClassifier: sin llamadas reales a Claude.

    Por defecto "clasifica" como el primer tipo permitido con confianza
    alta; ajusta `result` antes de la llamada para probar otros casos
    (sin clasificar, baja confianza...).
    """

    def __init__(self) -> None:
        self.result: ClassificationResult | None = None
        self.calls: list[RecordedClassification] = []

    async def classify(
        self, content: bytes, content_type: str, allowed_type_names: list[str]
    ) -> ClassificationResult:
        self.calls.append(
            RecordedClassification(content_type=content_type, allowed_type_names=allowed_type_names)
        )
        if self.result is not None:
            return self.result
        if allowed_type_names:
            return ClassificationResult(document_type_name=allowed_type_names[0], confidence=0.95)
        return ClassificationResult(document_type_name=None, confidence=0.0)


def unclassified_result() -> ClassificationResult:
    return ClassificationResult(document_type_name=None, confidence=0.1)


class FakeBookContentGenerator:
    """Doble de prueba de BookContentGenerator: contenido determinista y sin
    llamadas reales a Claude, para probar el pipeline de BookGenerationService
    de punta a punta rápido y sin coste (ver ADR 0014).

    `fail_at` simula un fallo de la etapa correspondiente (para probar que
    el pipeline persiste BookStatus.FAILED con el trabajo previo intacto).
    """

    def __init__(self, chapter_count: int = 2, fail_at: str | None = None) -> None:
        self.chapter_count = chapter_count
        self.fail_at = fail_at

    async def research_market(
        self, topic: str, niche: str, target_audience: str, language: str
    ) -> MarketResearchResult:
        if self.fail_at == "research":
            raise RuntimeError("fallo simulado en investigación de mercado")
        return MarketResearchResult(
            summary=f"Resumen de mercado para {topic}",
            trending_angles=["ángulo con demanda 1", "ángulo con demanda 2"],
            competitor_titles=["Libro competidor de ejemplo"],
            recommended_keywords=["palabra clave 1", "palabra clave 2"],
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
        if self.fail_at == "title":
            raise RuntimeError("fallo simulado generando título")
        return TitleSuggestion(title=f"Título de prueba sobre {topic}", subtitle="Un subtítulo")

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
        if self.fail_at == "outline":
            raise RuntimeError("fallo simulado generando esquema")
        return [
            ChapterOutline(
                order=i,
                title=f"Capítulo {i}",
                summary=f"Resumen del capítulo {i}",
                target_word_count=150,
            )
            for i in range(1, self.chapter_count + 1)
        ]

    async def write_chapter(
        self, book_title: str, style: str, language: str, chapter: ChapterOutline
    ) -> str:
        if self.fail_at == "chapters":
            raise RuntimeError("fallo simulado escribiendo capítulo")
        return f"Contenido en bruto del capítulo '{chapter.title}' para '{book_title}'."

    async def edit_chapter(self, content: str, language: str) -> str:
        if self.fail_at == "editing":
            raise RuntimeError("fallo simulado editando capítulo")
        return f"{content} (editado)"

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
        if self.fail_at == "sales_copy":
            raise RuntimeError("fallo simulado generando copy comercial")
        return SalesCopyResult(
            blurb="Descripción comercial de prueba, lista para publicar.",
            seo_keywords=["seo uno", "seo dos"],
            categories=["Categoría de prueba"],
        )

    async def generate_cover_brief(
        self, title: str, subtitle: str, niche: str, style: str, language: str
    ) -> str:
        if self.fail_at == "cover_brief":
            raise RuntimeError("fallo simulado generando brief de portada")
        return "Brief de portada de prueba: composición minimalista, paleta azul."
