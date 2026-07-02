from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.orders.entity import Order
from src.modules.orders.mapper import OrderMapper
from src.modules.orders.models import OrderModel


class OrderRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, order: Order) -> Order:
        mapped_order = OrderMapper.to_model(order)
        self.db_session.add(mapped_order)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_order)
        return OrderMapper.to_entity(mapped_order)

    async def get_all(self) -> List[Order]:
        query = select(OrderModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [OrderMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Order | None:
        model = await self.db_session.get(OrderModel, id)

        if model is None:
            return None

        return OrderMapper.to_entity(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[Order]:
        query = select(OrderModel).where(OrderModel.user_id == user_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [OrderMapper.to_entity(model) for model in models]

    async def update_by_id(self, order: Order) -> Order | None:
        model = OrderMapper.to_model(order)
        db_order = await self.db_session.merge(model)

        if db_order is None:
            return None

        await self.db_session.flush()

        return OrderMapper.to_entity(db_order)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(OrderModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
