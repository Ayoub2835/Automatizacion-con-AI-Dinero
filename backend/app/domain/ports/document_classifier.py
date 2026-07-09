from dataclasses import dataclass
from typing import Protocol


@dataclass
class ClassificationResult:
    document_type_name: str | None
    confidence: float


class DocumentClassifier(Protocol):
    """Puerto para clasificar un documento entre los tipos que pide una campaña.

    `document_type_name` es None cuando el clasificador no encuentra una
    correspondencia clara (ver ADR 0011).
    """

    async def classify(
        self, content: bytes, content_type: str, allowed_type_names: list[str]
    ) -> ClassificationResult: ...
