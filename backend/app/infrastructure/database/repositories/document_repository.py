from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.document import Document, DocumentStatus
from app.infrastructure.database.models.document import DocumentModel


class SqlAlchemyDocumentRepository:
    """Implementación concreta de DocumentRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, document: Document) -> Document:
        model = DocumentModel(
            id=document.id,
            campaign_client_id=document.campaign_client_id,
            campaign_document_type_id=document.campaign_document_type_id,
            original_filename=document.original_filename,
            storage_path=document.storage_path,
            content_type=document.content_type,
            status=document.status,
            classification_confidence=document.classification_confidence,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def list_for_campaign_clients(self, campaign_client_ids: list[UUID]) -> list[Document]:
        if not campaign_client_ids:
            return []
        result = await self._session.execute(
            select(DocumentModel)
            .where(DocumentModel.campaign_client_id.in_(campaign_client_ids))
            .order_by(DocumentModel.uploaded_at)
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: DocumentModel) -> Document:
        return Document(
            id=model.id,
            campaign_client_id=model.campaign_client_id,
            campaign_document_type_id=model.campaign_document_type_id,
            original_filename=model.original_filename,
            storage_path=model.storage_path,
            content_type=model.content_type,
            status=DocumentStatus(model.status),
            classification_confidence=model.classification_confidence,
            uploaded_at=model.uploaded_at,
        )
