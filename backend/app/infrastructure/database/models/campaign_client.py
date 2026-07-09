import uuid
from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.domain.entities.campaign_client import CampaignClientStatus
from app.infrastructure.database.base import Base


class CampaignClientModel(Base):
    __tablename__ = "campaign_clients"
    __table_args__ = (UniqueConstraint("campaign_id", "client_id", name="uq_campaign_client"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("campaigns.id"), nullable=False, index=True
    )
    client_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("clients.id"), nullable=False, index=True
    )
    upload_token: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    status: Mapped[CampaignClientStatus] = mapped_column(
        SAEnum(
            CampaignClientStatus,
            name="campaign_client_status",
            native_enum=False,
            validate_strings=True,
        ),
        nullable=False,
        default=CampaignClientStatus.PENDING,
    )
    last_reminder_sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
