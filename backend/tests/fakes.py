from dataclasses import dataclass

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
