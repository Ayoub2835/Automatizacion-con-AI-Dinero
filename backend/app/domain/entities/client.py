from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID


@dataclass
class Client:
    """Un cliente de la gestoría (persona o empresa a la que se le pide documentación)."""

    id: UUID
    organization_id: UUID
    name: str
    email: str
    created_at: datetime
    phone: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
