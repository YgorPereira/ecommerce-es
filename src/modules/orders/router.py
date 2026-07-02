from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException
from src.modules.coupons.repository import CouponRepository
from src.modules.order_items.repository import OrderItemRepository
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import (
    CreateOrderSchema,
    UpdateOrderSchema,
    OrderResponseSchema,
)
from src.modules.orders.services import OrderService

order_router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


def get_order_service(
    db: Session = Depends(get_db),
) -> OrderService:
    repository = OrderRepository(db)
    return OrderService(
        repository,
        OrderItemRepository(db),
        CouponRepository(db),
    )


@order_router.post(
    "",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order(
    order: CreateOrderSchema,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    order.user_id = current_user.id
    return await service.create_order(order)


@order_router.get(
    "",
    response_model=List[OrderResponseSchema],
)
async def get_all_orders(
    service: OrderService = Depends(get_order_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_orders()


@order_router.get(
    "/{order_id}",
    response_model=OrderResponseSchema,
)
async def get_order_by_id(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    order = await service.get_order_by_id(order_id)
    if not current_user.is_admin() and order.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return order


@order_router.post(
    "/{order_id}/calculate-total",
    response_model=OrderResponseSchema,
)
async def calculate_order_total(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    return await service.calculate_order_total(order_id)


@order_router.get(
    "/user/{user_id}",
    response_model=List[OrderResponseSchema],
)
async def get_orders_by_user_id(
    user_id: UUID,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin() and current_user.id != user_id:
        raise UnauthorizedException("Acesso negado")
    return await service.get_orders_by_user_id(user_id)


@order_router.put(
    "",
    response_model=OrderResponseSchema,
)
async def update_order(
    order: UpdateOrderSchema,
    service: OrderService = Depends(get_order_service),
    _: User = Depends(require_admin),
):
    return await service.update_order(order)


@order_router.delete(
    "/{order_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order(
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
):
    await service.delete_order_by_id(order_id)
