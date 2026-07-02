from datetime import datetime, timezone
from typing import List
import uuid

from src.modules.carts.entity import Cart
from src.modules.carts.exceptions import CartNotFoundException
from src.modules.carts.repository import CartRepository
from src.modules.carts.schemas import CreateCartSchema, UpdateCartSchema


class CartService:
    def __init__(self, repository: CartRepository):
        self.repository = repository

    async def create_cart(self, cart: CreateCartSchema) -> Cart:
        return await self.repository.create(
            Cart(
                user_id=cart.user_id,
                coupon_id=cart.coupon_id,
                created_at=datetime.now(timezone.utc),
            )
        )

    async def get_all_carts(self) -> List[Cart]:
        return await self.repository.get_all()

    async def get_cart_by_id(self, id: uuid.UUID) -> Cart:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CartNotFoundException()

        return db_item

    async def get_carts_by_user_id(self, user_id: uuid.UUID) -> List[Cart]:
        return await self.repository.get_by_user_id(user_id)

    async def update_cart(self, cart: UpdateCartSchema) -> Cart | None:
        db_item = await self.repository.get_by_id(cart.id)

        if db_item is None:
            raise CartNotFoundException()

        return await self.repository.update_by_id(
            Cart(
                id=cart.id,
                user_id=cart.user_id,
                coupon_id=cart.coupon_id,
                created_at=db_item.created_at,
            )
        )

    async def delete_cart_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CartNotFoundException()

        return await self.repository.delete_by_id(id)
