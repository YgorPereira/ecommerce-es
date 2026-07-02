from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.payments.entity import Payment
from src.modules.payments.mapper import PaymentMapper
from src.modules.payments.models import PaymentModel


class PaymentRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, payment: Payment) -> Payment:
        mapped_payment = PaymentMapper.to_model(payment)
        self.db_session.add(mapped_payment)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_payment)
        return PaymentMapper.to_entity(mapped_payment)

    async def get_all(self) -> List[Payment]:
        query = select(PaymentModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [PaymentMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Payment | None:
        model = await self.db_session.get(PaymentModel, id)

        if model is None:
            return None

        return PaymentMapper.to_entity(model)

    async def get_by_reference(self, reference: str) -> Payment | None:
        query = select(PaymentModel).where(PaymentModel.gateway_reference == reference)
        model = await self.db_session.scalar(query)

        if model is None:
            return None

        return PaymentMapper.to_entity(model)

    async def get_by_order_id(self, order_id: uuid.UUID) -> List[Payment]:
        query = select(PaymentModel).where(PaymentModel.order_id == order_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [PaymentMapper.to_entity(model) for model in models]

    async def update_by_id(self, payment: Payment) -> Payment | None:
        model = PaymentMapper.to_model(payment)
        db_payment = await self.db_session.merge(model)

        if db_payment is None:
            return None

        await self.db_session.flush()

        return PaymentMapper.to_entity(db_payment)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(PaymentModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
