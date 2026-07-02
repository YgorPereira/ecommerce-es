from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.shared.exceptions import UnauthorizedException
from src.modules.cart_items.repository import CartItemRepository
from src.modules.cart_items.schemas import (
    CreateCartItemSchema,
    UpdateCartItemSchema,
    CartItemResponseSchema,
)
from src.modules.cart_items.services import CartItemService

cart_item_router = APIRouter(
    prefix="/cart_items",
    tags=["Cart Items"],
)


def get_cart_item_service(
    db: Session = Depends(get_db),
) -> CartItemService:
    repository = CartItemRepository(db)
    return CartItemService(repository)


@cart_item_router.post(
    "",
    response_model=CartItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_cart_item(
    cart_item: CreateCartItemSchema,
    service: CartItemService = Depends(get_cart_item_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_cart_item(cart_item)


@cart_item_router.get(
    "",
    response_model=List[CartItemResponseSchema],
)
async def get_all_cart_items(
    service: CartItemService = Depends(get_cart_item_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_cart_items()


@cart_item_router.get(
    "/{cart_item_id}",
    response_model=CartItemResponseSchema,
)
async def get_cart_item_by_id(
    cart_item_id: UUID,
    service: CartItemService = Depends(get_cart_item_service),
):
    return await service.get_cart_item_by_id(cart_item_id)


@cart_item_router.get(
    "/cart/{cart_id}",
    response_model=List[CartItemResponseSchema],
)
async def get_cart_items_by_cart_id(
    cart_id: UUID,
    service: CartItemService = Depends(get_cart_item_service),
):
    return await service.get_cart_items_by_cart_id(cart_id)


@cart_item_router.put(
    "",
    response_model=CartItemResponseSchema,
)
async def update_cart_item(
    cart_item: UpdateCartItemSchema,
    service: CartItemService = Depends(get_cart_item_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_cart_item(cart_item)


@cart_item_router.delete(
    "/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart_item(
    cart_item_id: UUID,
    service: CartItemService = Depends(get_cart_item_service),
    current_user: User = Depends(get_current_user),
):
    await service.delete_cart_item_by_id(cart_item_id)
