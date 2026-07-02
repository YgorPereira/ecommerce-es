from typing import List
import uuid

from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.exceptions import CartItemNotFoundException
from src.modules.cart_items.mapper import CartItemMapper
from src.modules.cart_items.repository import CartItemRepository
from src.modules.cart_items.schemas import (
    CreateCartItemSchema,
    UpdateCartItemSchema,
)


class CartItemService:
    def __init__(self, repository: CartItemRepository):
        self.repository = repository

    async def create_cart_item(self, cart_item: CreateCartItemSchema) -> CartItem:
        return await self.repository.create(
            CartItemMapper.from_create_schema(cart_item)
        )

    async def get_all_cart_items(self) -> List[CartItem]:
        return await self.repository.get_all()

    async def get_cart_item_by_id(self, id: uuid.UUID) -> CartItem:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CartItemNotFoundException()

        return db_item

    async def get_cart_items_by_cart_id(self, cart_id: uuid.UUID) -> List[CartItem]:
        return await self.repository.get_by_cart_id(cart_id)

    async def update_cart_item(
        self, cart_item: UpdateCartItemSchema
    ) -> CartItem | None:
        db_item = await self.repository.get_by_id(cart_item.id)

        if db_item is None:
            raise CartItemNotFoundException()

        return await self.repository.update_by_id(
            CartItem(
                id=cart_item.id,
                cart_id=cart_item.cart_id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
            )
        )

    async def delete_cart_item_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CartItemNotFoundException()

        return await self.repository.delete_by_id(id)
