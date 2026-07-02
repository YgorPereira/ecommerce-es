from datetime import datetime, timezone
from typing import List
import uuid

from src.modules.orders.entity import Order
from src.modules.orders.exceptions import OrderNotFoundException
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import CreateOrderSchema, UpdateOrderSchema

DEFAULT_ORDER_STATUS = "pending"


class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repository = repository

    async def create_order(self, order: CreateOrderSchema) -> Order:
        return await self.repository.create(
            Order(
                user_id=order.user_id,
                address_id=order.address_id,
                coupon_id=order.coupon_id,
                total_amount=order.total_amount,
                status=DEFAULT_ORDER_STATUS,
                created_at=datetime.now(timezone.utc),
            )
        )

    async def get_all_orders(self) -> List[Order]:
        return await self.repository.get_all()

    async def get_order_by_id(self, id: uuid.UUID) -> Order:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise OrderNotFoundException()

        return db_item

    async def get_orders_by_user_id(self, user_id: uuid.UUID) -> List[Order]:
        return await self.repository.get_by_user_id(user_id)

    async def update_order(self, order: UpdateOrderSchema) -> Order | None:
        db_item = await self.repository.get_by_id(order.id)

        if db_item is None:
            raise OrderNotFoundException()

        return await self.repository.update_by_id(
            Order(
                id=order.id,
                user_id=order.user_id,
                address_id=order.address_id,
                coupon_id=order.coupon_id,
                total_amount=order.total_amount,
                status=order.status,
                created_at=db_item.created_at,
            )
        )

    async def delete_order_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise OrderNotFoundException()

        return await self.repository.delete_by_id(id)
