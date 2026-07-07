from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class Organization:
    """La gestoría: el tenant del sistema.

    `metadata` es un punto de extensión deliberado (ver ADR 0004): atributos
    específicos de una organización que aún no sabemos si merecen ser una
    columna propia viven aquí hasta que se demuestre lo contrario.
    """

    id: UUID
    name: str
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
