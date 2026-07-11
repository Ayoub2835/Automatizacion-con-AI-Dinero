from collections.abc import AsyncIterator
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.api.v1.routers.books as books_router
from app.api import deps as api_deps
from tests.fakes import FakeBookContentGenerator

_BOOK_PAYLOAD = {
    "topic": "Productividad para autónomos",
    "niche": "Negocios",
    "target_audience": "Autónomos que empiezan",
    "language": "español",
    "style": "cercano y práctico",
    "target_pages": 30,
}


class _NonClosingSessionContext:
    """Envuelve el `db_session` de test en el mismo protocolo async-context-
    manager que `AsyncSessionLocal()`, sin cerrarlo — así el BackgroundTask
    del pipeline de generación opera dentro de la misma transacción aislada
    del test en vez de abrir una conexión real nueva (ver conftest.py)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def __aenter__(self) -> AsyncSession:
        return self._session

    async def __aexit__(self, *exc_info: object) -> bool:
        return False


class _FakeSessionLocal:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def __call__(self) -> _NonClosingSessionContext:
        return _NonClosingSessionContext(self._session)


@pytest.fixture(autouse=True)
def _patch_generation_pipeline(
    db_session: AsyncSession, monkeypatch: pytest.MonkeyPatch
) -> AsyncIterator[None]:
    """Todos los tests de este módulo comparten la necesidad de que el
    BackgroundTask de generación (a) no llame a la API real de Claude y
    (b) vea los datos creados por la propia request de test (ver conftest.py
    sobre el aislamiento por transacción)."""
    monkeypatch.setattr(
        api_deps, "get_book_content_generator", lambda: FakeBookContentGenerator(chapter_count=2)
    )
    monkeypatch.setattr(books_router, "AsyncSessionLocal", _FakeSessionLocal(db_session))
    yield


async def _register_and_login(client: AsyncClient, email: str) -> str:
    await client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Editorial de prueba",
            "email": email,
            "password": "supersecret123",
        },
    )
    response = await client.post(
        "/api/v1/auth/login", json={"email": email, "password": "supersecret123"}
    )
    return str(response.json()["access_token"])


async def _create_book(client: AsyncClient, headers: dict[str, str]) -> dict[str, Any]:
    response = await client.post("/api/v1/books", json=_BOOK_PAYLOAD, headers=headers)
    assert response.status_code == 201
    return dict(response.json())


async def test_create_book_runs_pipeline_and_exports_files(client: AsyncClient) -> None:
    token = await _register_and_login(client, "autora@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = await _create_book(client, headers)

    get_response = await client.get(f"/api/v1/books/{created['id']}", headers=headers)
    assert get_response.status_code == 200
    book = get_response.json()

    # El pipeline encadena la exportación tras READY (ver run_generation_pipeline).
    assert book["status"] == "exported"
    assert book["generation_stage"] == "done"
    assert book["error_message"] is None
    assert book["title"]
    assert book["subtitle"]
    assert book["market_research"]["summary"]
    assert book["sales_blurb"]
    assert book["seo_keywords"]
    assert book["categories"]
    assert book["cover_brief"]
    assert book["has_epub"] is True
    assert book["has_pdf"] is True

    chapters_response = await client.get(f"/api/v1/books/{created['id']}/chapters", headers=headers)
    chapters = chapters_response.json()
    assert len(chapters) == 2
    assert all(c["status"] == "edited" for c in chapters)
    assert all(c["content"] for c in chapters)


async def test_generate_endpoint_rejects_book_that_is_not_draft_or_failed(
    client: AsyncClient,
) -> None:
    token = await _register_and_login(client, "autor2@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    created = await _create_book(client, headers)  # ya queda en READY tras la pipeline

    response = await client.post(f"/api/v1/books/{created['id']}/generate", headers=headers)
    assert response.status_code == 409


async def test_download_export_after_pipeline_completes(client: AsyncClient) -> None:
    token = await _register_and_login(client, "autor3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    created = await _create_book(client, headers)

    response = await client.get(f"/api/v1/books/{created['id']}/export/epub", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/epub+zip"


async def test_list_books_is_scoped_to_organization(client: AsyncClient) -> None:
    token_a = await _register_and_login(client, "editorial-a@example.com")
    token_b = await _register_and_login(client, "editorial-b@example.com")

    await _create_book(client, {"Authorization": f"Bearer {token_a}"})

    response = await client.get("/api/v1/books", headers={"Authorization": f"Bearer {token_b}"})
    assert response.status_code == 200
    assert response.json() == []
