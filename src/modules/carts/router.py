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
from src.modules.cart_items.router import get_cart_item_service
from src.modules.cart_items.schemas import CartItemResponseSchema
from src.modules.cart_items.services import CartItemService
from src.modules.carts.checkout import CheckoutService
from src.modules.carts.repository import CartRepository
from src.modules.carts.schemas import (
    CreateCartSchema,
    UpdateCartSchema,
    CartResponseSchema,
    CheckoutSchema,
)
from src.modules.carts.services import CartService
from src.modules.coupons.repository import CouponRepository
from src.modules.inventories.repository import InventoryRepository
from src.modules.order_items.repository import OrderItemRepository
from src.modules.orders.repository import OrderRepository
from src.modules.orders.schemas import OrderResponseSchema
from src.modules.products.repository import ProductRepository

cart_router = APIRouter(
    prefix="/carts",
    tags=["Carts"],
)


def get_cart_service(
    db: Session = Depends(get_db),
) -> CartService:
    repository = CartRepository(db)
    return CartService(repository)


def get_checkout_service(
    db: Session = Depends(get_db),
) -> CheckoutService:
    return CheckoutService(
        CartRepository(db),
        CartItemRepository(db),
        ProductRepository(db),
        InventoryRepository(db),
        CouponRepository(db),
        OrderRepository(db),
        OrderItemRepository(db),
    )


@cart_router.post(
    "",
    response_model=CartResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_cart(
    cart: CreateCartSchema,
    service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user),
):
    cart.user_id = current_user.id
    return await service.create_cart(cart)


@cart_router.get(
    "",
    response_model=List[CartResponseSchema],
)
async def get_all_carts(
    service: CartService = Depends(get_cart_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_carts()


@cart_router.get(
    "/{cart_id}",
    response_model=CartResponseSchema,
)
async def get_cart_by_id(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user),
):
    cart = await service.get_cart_by_id(cart_id)
    if not current_user.is_admin() and cart.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return cart


@cart_router.get(
    "/user/{user_id}",
    response_model=List[CartResponseSchema],
)
async def get_carts_by_user_id(
    user_id: UUID,
    service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user),
):
    if not current_user.is_admin() and current_user.id != user_id:
        raise UnauthorizedException("Acesso negado")
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


@cart_router.post(
    "/{cart_id}/checkout",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def checkout(
    cart_id: UUID,
    payload: CheckoutSchema,
    service: CheckoutService = Depends(get_checkout_service),
    current_user: User = Depends(get_current_user),
):
    cart = await service.cart_repository.get_by_id(cart_id)
    if not current_user.is_admin() and cart.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return await service.checkout(cart_id, payload.address_id)


@cart_router.put(
    "",
    response_model=CartResponseSchema,
)
async def update_cart(
    cart: UpdateCartSchema,
    service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user),
):
    db_cart = await service.repository.get_by_id(cart.id)
    if not current_user.is_admin() and db_cart.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    return await service.update_cart(cart)


@cart_router.delete(
    "/{cart_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_cart(
    cart_id: UUID,
    service: CartService = Depends(get_cart_service),
    current_user: User = Depends(get_current_user),
):
    cart = await service.get_cart_by_id(cart_id)
    if not current_user.is_admin() and cart.user_id != current_user.id:
        raise UnauthorizedException("Acesso negado")
    await service.delete_cart_by_id(cart_id)
