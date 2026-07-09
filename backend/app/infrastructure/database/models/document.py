import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.domain.entities.document import DocumentStatus
from app.infrastructure.database.base import Base


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaign_clients.id"), nullable=False, index=True
    )
    campaign_document_type_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("campaign_document_types.id"), nullable=True, index=True
    )
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    storage_path: Mapped[str] = mapped_column(String, nullable=False)
    content_type: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(
        SAEnum(DocumentStatus, name="document_status", native_enum=False, validate_strings=True),
        nullable=False,
        default=DocumentStatus.UNCLASSIFIED,
    )
    classification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
