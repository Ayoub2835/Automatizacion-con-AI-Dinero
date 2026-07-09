"""Importar todos los modelos aquí para que Base.metadata los conozca
(usado por Alembic y por los tests al crear el esquema)."""

from app.infrastructure.database.models.client import ClientModel
from app.infrastructure.database.models.organization import OrganizationModel
from app.infrastructure.database.models.user import UserModel

__all__ = ["ClientModel", "OrganizationModel", "UserModel"]
