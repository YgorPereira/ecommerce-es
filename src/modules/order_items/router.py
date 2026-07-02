from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.order_items.repository import OrderItemRepository
from src.modules.order_items.schemas import (
    CreateOrderItemSchema,
    UpdateOrderItemSchema,
    OrderItemResponseSchema,
)
from src.modules.order_items.services import OrderItemService

order_item_router = APIRouter(
    prefix="/order_items",
    tags=["Order Items"],
)


def get_order_item_service(
    db: Session = Depends(get_db),
) -> OrderItemService:
    repository = OrderItemRepository(db)
    return OrderItemService(repository)


@order_item_router.post(
    "",
    response_model=OrderItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_order_item(
    order_item: CreateOrderItemSchema,
    service: OrderItemService = Depends(get_order_item_service),
):
    return await service.create_order_item(order_item)


@order_item_router.get(
    "",
    response_model=List[OrderItemResponseSchema],
)
async def get_all_order_items(
    service: OrderItemService = Depends(get_order_item_service),
):
    return await service.get_all_order_items()


@order_item_router.get(
    "/{order_item_id}",
    response_model=OrderItemResponseSchema,
)
async def get_order_item_by_id(
    order_item_id: UUID,
    service: OrderItemService = Depends(get_order_item_service),
):
    return await service.get_order_item_by_id(order_item_id)


@order_item_router.get(
    "/order/{order_id}",
    response_model=List[OrderItemResponseSchema],
)
async def get_order_items_by_order_id(
    order_id: UUID,
    service: OrderItemService = Depends(get_order_item_service),
):
    return await service.get_order_items_by_order_id(order_id)


@order_item_router.put(
    "",
    response_model=OrderItemResponseSchema,
)
async def update_order_item(
    order_item: UpdateOrderItemSchema,
    service: OrderItemService = Depends(get_order_item_service),
):
    return await service.update_order_item(order_item)


@order_item_router.delete(
    "/{order_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_order_item(
    order_item_id: UUID,
    service: OrderItemService = Depends(get_order_item_service),
):
    await service.delete_order_item_by_id(order_item_id)
