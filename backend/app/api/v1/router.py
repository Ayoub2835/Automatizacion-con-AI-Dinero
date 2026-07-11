from fastapi import APIRouter

from app.api.v1.routers import auth, books, campaigns, clients, health, public, publishing

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(clients.router, prefix="/clients", tags=["clients"])
api_router.include_router(campaigns.router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(books.router, prefix="/books", tags=["books"])
api_router.include_router(publishing.router, tags=["publishing"])
