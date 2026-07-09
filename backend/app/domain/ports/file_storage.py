from typing import Protocol
from uuid import UUID


class FileStorage(Protocol):
    """Puerto para guardar/leer los ficheros subidos. Ver ADR 0010."""

    async def save(self, campaign_client_id: UUID, filename: str, content: bytes) -> str:
        """Guarda el fichero y devuelve su storage_path (opaco, no una URL pública)."""
        ...

    async def read(self, storage_path: str) -> bytes: ...
