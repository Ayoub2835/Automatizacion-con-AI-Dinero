import os
import tempfile
from collections.abc import AsyncGenerator

# Los documentos subidos en los tests van a un directorio temporal, no al
# UPLOADS_DIR real — debe fijarse antes de que algo importe app.core.config.
os.environ.setdefault("UPLOADS_DIR", tempfile.mkdtemp(prefix="gestoria-test-uploads-"))

import pytest_asyncio  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402
from sqlalchemy.ext.asyncio import (  # noqa: E402
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_db_session, get_document_classifier, get_email_sender  # noqa: E402
from app.core.config import get_settings  # noqa: E402
from app.infrastructure.database.base import Base  # noqa: E402
from app.infrastructure.database.models import OrganizationModel, UserModel  # noqa: E402, F401
from app.main import app  # noqa: E402
from tests.fakes import FakeDocumentClassifier, FakeEmailSender  # noqa: E402

settings = get_settings()


@pytest_asyncio.fixture(scope="session")
async def engine() -> AsyncGenerator[AsyncEngine, None]:
    test_engine = create_async_engine(settings.database_url)
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield test_engine
    await test_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Aísla cada test en su propia transacción, revertida al terminar."""
    connection = await engine.connect()
    transaction = await connection.begin()
    session_factory = async_sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    session = session_factory()

    try:
        yield session
    finally:
        await session.close()
        await transaction.rollback()
        await connection.close()


@pytest_asyncio.fixture
def email_sender() -> FakeEmailSender:
    """Doble en memoria de EmailSender, inyectado en el cliente de test."""
    return FakeEmailSender()


@pytest_asyncio.fixture
def document_classifier() -> FakeDocumentClassifier:
    """Doble en memoria de DocumentClassifier, inyectado en el cliente de test."""
    return FakeDocumentClassifier()


@pytest_asyncio.fixture
async def client(
    db_session: AsyncSession,
    email_sender: FakeEmailSender,
    document_classifier: FakeDocumentClassifier,
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    app.dependency_overrides[get_document_classifier] = lambda: document_classifier
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
