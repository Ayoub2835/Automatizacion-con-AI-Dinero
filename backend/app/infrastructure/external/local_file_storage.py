import asyncio
import re
import uuid
from pathlib import Path
from uuid import UUID

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9._-]")


class LocalFileStorage:
    """Implementación concreta de FileStorage sobre el disco local (ver ADR 0010).

    Cada fichero se guarda bajo `<base_dir>/<campaign_client_id>/<uuid>_<nombre-saneado>`:
    el prefijo UUID evita colisiones de nombre y el saneado evita path
    traversal a partir de un nombre de fichero controlado por el cliente.
    """

    def __init__(self, base_dir: str) -> None:
        self._base_dir = Path(base_dir)

    async def save(self, campaign_client_id: UUID, filename: str, content: bytes) -> str:
        safe_name = _UNSAFE_CHARS.sub("_", filename).strip("._") or "documento"
        safe_name = safe_name[-100:]
        relative_path = Path(str(campaign_client_id)) / f"{uuid.uuid4()}_{safe_name}"
        full_path = self._base_dir / relative_path

        def _write() -> None:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_bytes(content)

        await asyncio.to_thread(_write)
        return str(relative_path)

    async def read(self, storage_path: str) -> bytes:
        full_path = self._base_dir / storage_path
        return await asyncio.to_thread(full_path.read_bytes)
