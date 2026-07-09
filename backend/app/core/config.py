from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación, cargada desde variables de entorno.

    Ver .env.example en la raíz del repositorio para la lista completa de
    variables y su documentación.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: Literal["development", "test", "staging", "production"] = "development"
    log_level: str = "INFO"

    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    database_url: str

    backend_cors_origins: list[str] = ["http://localhost:3000"]

    # URL pública del panel, usada para construir enlaces que un humano abre
    # en su propio navegador (ej. el enlace seguro de subida de documentos
    # en el email). No confundir con API_URL del frontend, que es interno.
    frontend_url: str = "http://localhost:3000"

    # SMTP genérico (ver ADR 0009): sin vendor lock-in, cualquier proveedor
    # (Gmail, SendGrid, Amazon SES...) o un servidor local de pruebas sirve.
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = False
    smtp_from_email: str = "no-reply@gestoria.local"

    # Directorio donde se guardan los documentos subidos (ver ADR 0010).
    uploads_dir: str = "uploads"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
