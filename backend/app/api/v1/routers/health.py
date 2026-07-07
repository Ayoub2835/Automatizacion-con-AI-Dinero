from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Usado por Docker/orquestadores para comprobar que el servicio está vivo."""
    return {"status": "ok"}
