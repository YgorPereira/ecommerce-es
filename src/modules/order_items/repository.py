from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.order_items.entity import OrderItem
from src.modules.order_items.mapper import OrderItemMapper
from src.modules.order_items.models import OrderItemModel


class OrderItemRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, order_item: OrderItem) -> OrderItem:
        mapped_order_item = OrderItemMapper.to_model(order_item)
        self.db_session.add(mapped_order_item)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_order_item)
        return OrderItemMapper.to_entity(mapped_order_item)

    async def get_all(self) -> List[OrderItem]:
        query = select(OrderItemModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [OrderItemMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> OrderItem | None:
        model = await self.db_session.get(OrderItemModel, id)

        if model is None:
            return None

        return OrderItemMapper.to_entity(model)

    async def get_by_order_id(self, order_id: uuid.UUID) -> List[OrderItem]:
        query = select(OrderItemModel).where(OrderItemModel.order_id == order_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [OrderItemMapper.to_entity(model) for model in models]

    async def update_by_id(self, order_item: OrderItem) -> OrderItem | None:
        model = OrderItemMapper.to_model(order_item)
        db_order_item = await self.db_session.merge(model)

        if db_order_item is None:
            return None

        await self.db_session.flush()

        return OrderItemMapper.to_entity(db_order_item)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(OrderItemModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
