from datetime import datetime, timezone
from typing import List
import uuid

from src.modules.coupons.exceptions import CouponNotFoundException
from src.modules.coupons.repository import CouponRepository
from src.modules.coupons.validation import assert_coupon_applicable
from src.modules.order_items.repository import OrderItemRepository
from src.modules.orders.entity import Order
from src.modules.orders.exceptions import (
    OrderAlreadyPaidException,
    OrderNotFoundException,
)
from src.modules.orders.pricing import LineItem, calculate_total
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import CreateOrderSchema, UpdateOrderSchema

DEFAULT_ORDER_STATUS = "pending"
PAID_ORDER_STATUS = "paid"


class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        order_item_repository: OrderItemRepository,
        coupon_repository: CouponRepository,
    ):
        self.repository = repository
        self.order_item_repository = order_item_repository
        self.coupon_repository = coupon_repository

    async def calculate_order_total(self, order_id: uuid.UUID) -> Order:
        """Recalcula o total do pedido no servidor (fonte da verdade).

        Soma os itens do pedido e aplica o cupom — validando validade e usos.
        O total nunca é confiado ao cliente.
        """
        order = await self.get_order_by_id(order_id)

        items = await self.order_item_repository.get_by_order_id(order_id)
        line_items = [
            LineItem(price=item.price, quantity=item.quantity) for item in items
        ]

        coupon = None
        if order.coupon_id is not None:
            coupon = await self.coupon_repository.get_by_id(order.coupon_id)

            if coupon is None:
                raise CouponNotFoundException()

            assert_coupon_applicable(coupon, datetime.now(timezone.utc))

        total = calculate_total(line_items, coupon)

        return await self.repository.update_by_id(
            Order(
                id=order.id,
                user_id=order.user_id,
                address_id=order.address_id,
                coupon_id=order.coupon_id,
                total_amount=total,
                status=order.status,
                created_at=order.created_at,
            )
        )

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

        if db_item.status == PAID_ORDER_STATUS:
            raise OrderAlreadyPaidException()

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

        if db_item.status == PAID_ORDER_STATUS:
            raise OrderAlreadyPaidException()

        return await self.repository.delete_by_id(id)
