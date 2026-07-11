import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    AlreadyExistsError,
    DomainError,
    EntityNotFoundError,
    InvalidCredentialsError,
)

logger = logging.getLogger(__name__)

_STATUS_BY_EXCEPTION: dict[type[DomainError], int] = {
    EntityNotFoundError: status.HTTP_404_NOT_FOUND,
    AlreadyExistsError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
}


def register_exception_handlers(app: FastAPI) -> None:
    """Traduce excepciones de dominio a respuestas HTTP consistentes.

    Cualquier excepción de dominio nueva que no esté en _STATUS_BY_EXCEPTION
    se traduce a 400 por defecto — hay que registrarla explícitamente aquí
    si necesita otro código.
    """

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status_code = _STATUS_BY_EXCEPTION.get(type(exc), status.HTTP_400_BAD_REQUEST)
        logger.info(
            "domain_error",
            extra={"error_type": type(exc).__name__, "path": request.url.path},
        )
        return JSONResponse(
            status_code=status_code,
            content={"detail": str(exc), "error": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_exception", extra={"path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": "InternalServerError"},
        )
