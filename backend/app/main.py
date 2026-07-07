from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging

configure_logging()
settings = get_settings()

app = FastAPI(
    title="GestorIA API",
    version="0.1.0",
    description=(
        "API base del SaaS de IA para gestorías. "
        "Fase de fundación técnica: sin funcionalidades de negocio todavía."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")
