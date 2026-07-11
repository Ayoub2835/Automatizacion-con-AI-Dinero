from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.publishing import SalesRecord
from app.infrastructure.database.models.publishing import SalesRecordModel


class SqlAlchemySalesRecordRepository:
    """Implementación concreta de SalesRecordRepository sobre SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, sales_record: SalesRecord) -> SalesRecord:
        model = SalesRecordModel(
            id=sales_record.id,
            organization_id=sales_record.organization_id,
            publication_id=sales_record.publication_id,
            period_start=sales_record.period_start,
            period_end=sales_record.period_end,
            units_sold=sales_record.units_sold,
            revenue_amount=sales_record.revenue_amount,
            currency=sales_record.currency,
            source=sales_record.source,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_entity(model)

    async def list_for_organization(self, organization_id: UUID) -> list[SalesRecord]:
        result = await self._session.execute(
            select(SalesRecordModel)
            .where(SalesRecordModel.organization_id == organization_id)
            .order_by(SalesRecordModel.period_start.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    async def list_for_publication(
        self, publication_id: UUID, organization_id: UUID
    ) -> list[SalesRecord]:
        result = await self._session.execute(
            select(SalesRecordModel)
            .where(
                SalesRecordModel.publication_id == publication_id,
                SalesRecordModel.organization_id == organization_id,
            )
            .order_by(SalesRecordModel.period_start.desc())
        )
        return [self._to_entity(m) for m in result.scalars().all()]

    @staticmethod
    def _to_entity(model: SalesRecordModel) -> SalesRecord:
        return SalesRecord(
            id=model.id,
            organization_id=model.organization_id,
            publication_id=model.publication_id,
            period_start=model.period_start,
            period_end=model.period_end,
            units_sold=model.units_sold,
            revenue_amount=model.revenue_amount,
            currency=model.currency,
            source=model.source,
            recorded_at=model.recorded_at,
        )
