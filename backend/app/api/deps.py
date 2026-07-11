from collections.abc import AsyncGenerator
from uuid import UUID

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.security import decode_token
from app.domain.entities.user import User
from app.domain.exceptions import InvalidCredentialsError
from app.domain.ports.document_classifier import DocumentClassifier
from app.domain.ports.email_sender import EmailSender
from app.infrastructure.database.repositories.user_repository import SqlAlchemyUserRepository
from app.infrastructure.database.session import get_session
from app.infrastructure.external.claude_document_classifier import ClaudeDocumentClassifier
from app.infrastructure.external.smtp_email_sender import SmtpEmailSender

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=True)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db_session),
) -> User:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise InvalidCredentialsError() from exc

    user_repo = SqlAlchemyUserRepository(session)
    user = await user_repo.get_by_id(UUID(payload["sub"]))
    if user is None:
        raise InvalidCredentialsError()
    return user


def get_email_sender() -> EmailSender:
    return SmtpEmailSender(get_settings())


def get_document_classifier() -> DocumentClassifier:
    return ClaudeDocumentClassifier(get_settings().anthropic_api_key)
