from typing import List
import uuid

from src.modules.order_items.entity import OrderItem
from src.modules.order_items.exceptions import OrderItemNotFoundException
from src.modules.order_items.mapper import OrderItemMapper
from src.modules.order_items.repository import OrderItemRepository
from src.modules.order_items.schemas import (
    CreateOrderItemSchema,
    UpdateOrderItemSchema,
)


class OrderItemService:
    def __init__(self, repository: OrderItemRepository):
        self.repository = repository

    async def create_order_item(self, order_item: CreateOrderItemSchema) -> OrderItem:
        return await self.repository.create(
            OrderItemMapper.from_create_schema(order_item)
        )

    async def get_all_order_items(self) -> List[OrderItem]:
        return await self.repository.get_all()

    async def get_order_item_by_id(self, id: uuid.UUID) -> OrderItem:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise OrderItemNotFoundException()

        return db_item

    async def get_order_items_by_order_id(self, order_id: uuid.UUID) -> List[OrderItem]:
        return await self.repository.get_by_order_id(order_id)

    async def update_order_item(
        self, order_item: UpdateOrderItemSchema
    ) -> OrderItem | None:
        db_item = await self.repository.get_by_id(order_item.id)

        if db_item is None:
            raise OrderItemNotFoundException()

        return await self.repository.update_by_id(
            OrderItem(
                id=order_item.id,
                order_id=order_item.order_id,
                product_id=order_item.product_id,
                quantity=order_item.quantity,
                price=order_item.price,
            )
        )

    async def delete_order_item_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise OrderItemNotFoundException()

        return await self.repository.delete_by_id(id)
