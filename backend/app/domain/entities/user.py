from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID


class UserRole(StrEnum):
    ADMIN = "admin"
    MEMBER = "member"


@dataclass
class User:
    """Un miembro de una gestoría (Organization).

    El email es único a nivel global del sistema (no por organización): un
    usuario inicia sesión sin tener que indicar antes a qué organización
    pertenece. Ver `docs/architecture/authentication.md`.
    """

    id: UUID
    organization_id: UUID
    email: str
    hashed_password: str
    role: UserRole
    created_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)
