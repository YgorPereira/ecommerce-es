from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.cart_items.router import get_cart_item_service
from src.modules.cart_items.schemas import CartItemResponseSchema
from src.modules.cart_items.services import CartItemService
from src.modules.carts.repository import CartRepository
from src.modules.carts.schemas import (
    CreateCartSchema,
    UpdateCartSchema,
    CartResponseSchema,
)
from src.modules.carts.services import CartService

cart_router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)


def get_cart_service(
    db: Session = Depends(get_db),
) -> CartService:
    repository = CartRepository(db)
    return CartService(repository)


@cart_router.post(
    "",
    response_model=CartResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_cart(
    cart: CreateCartSchema,
    service: CartService = Depends(get_cart_service),
):
    return await service.create_cart(cart)


@cart_router.get(
    "",
    response_model=List[CartResponseSchema],
)
async def get_all_carts(
    service: CartService = Depends(get_cart_service),
):
    return await service.get_all_carts()


@cart_router.get(
    "/{cart_id}",
    response_model=CartResponseSchema,
)
async def get_cart_by_id(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
):
    return await service.get_cart_by_id(cart_id)


@cart_router.get(
    "/user/{user_id}",
    response_model=List[CartResponseSchema],
)
async def get_carts_by_user_id(
    user_id: UUID,
    service: CartService = Depends(get_cart_service),
):
    return await service.get_carts_by_user_id(user_id)


@cart_router.get(
    "/{cart_id}/items",
    response_model=List[CartItemResponseSchema],
)
async def get_cart_items(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
    cart_item_service: CartItemService = Depends(get_cart_item_service),
):
    await service.get_cart_by_id(cart_id)
    return await cart_item_service.get_cart_items_by_cart_id(cart_id)


@cart_router.put(
    "",
    response_model=CartResponseSchema,
)
async def update_cart(
    cart: UpdateCartSchema,
    service: CartService = Depends(get_cart_service),
):
    return await service.update_cart(cart)


@cart_router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
):
    await service.delete_cart_by_id(cart_id)
