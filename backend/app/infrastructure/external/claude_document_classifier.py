import base64
import json
from typing import Any

import anthropic

from app.domain.ports.document_classifier import ClassificationResult

_MODEL = "claude-opus-4-8"
_MAX_TOKENS = 256


class ClaudeDocumentClassifier:
    """Implementación concreta de DocumentClassifier sobre la API de Claude.

    Usa structured outputs (`output_config.format`) para forzar un JSON con
    el tipo de documento (restringido a los tipos que pide la campaña, más
    "unknown") y una confianza — ver ADR 0011.
    """

    def __init__(self, api_key: str | None) -> None:
        # El cliente se construye dentro de classify(), no aquí: así, si falta
        # la API key, el error ocurre dentro del try/except del llamador
        # (PublicCampaignService) en vez de al resolver la dependencia FastAPI.
        self._api_key = api_key

    async def classify(
        self, content: bytes, content_type: str, allowed_type_names: list[str]
    ) -> ClassificationResult:
        client = anthropic.AsyncAnthropic(api_key=self._api_key)
        schema: dict[str, Any] = {
            "type": "object",
            "properties": {
                "document_type": {
                    "type": "string",
                    "enum": [*allowed_type_names, "unknown"],
                },
                "confidence": {"type": "number"},
            },
            "required": ["document_type", "confidence"],
            "additionalProperties": False,
        }

        messages = [
            {
                "role": "user",
                "content": [
                    self._build_content_block(content, content_type),
                    {
                        "type": "text",
                        "text": (
                            "Clasifica este documento en uno de estos tipos: "
                            f"{', '.join(allowed_type_names)}. "
                            'Si no encaja claramente con ninguno, responde "unknown". '
                            "Indica tu confianza entre 0 y 1."
                        ),
                    },
                ],
            }
        ]
        # El SDK tipa `messages`/`output_config` con TypedDicts precisos; los
        # dicts planos (la forma idiomática documentada por Anthropic) son
        # estructuralmente válidos en tiempo de ejecución pero mypy estricto
        # no lo infiere sin anotar cada bloque como su TypedDict exacto.
        response = await client.messages.create(  # type: ignore[call-overload]
            model=_MODEL,
            max_tokens=_MAX_TOKENS,
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=messages,
        )

        text = next(block.text for block in response.content if block.type == "text")
        parsed = json.loads(text)
        document_type = parsed["document_type"]
        return ClassificationResult(
            document_type_name=None if document_type == "unknown" else document_type,
            confidence=float(parsed["confidence"]),
        )

    @staticmethod
    def _build_content_block(content: bytes, content_type: str) -> dict[str, Any]:
        encoded = base64.b64encode(content).decode("ascii")
        block_type = "document" if content_type == "application/pdf" else "image"
        return {
            "type": block_type,
            "source": {"type": "base64", "media_type": content_type, "data": encoded},
        }
