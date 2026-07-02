from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.mapper import CartItemMapper
from src.modules.cart_items.models import CartItemModel


class CartItemRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, cart_item: CartItem) -> CartItem:
        mapped_cart_item = CartItemMapper.to_model(cart_item)
        self.db_session.add(mapped_cart_item)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_cart_item)
        return CartItemMapper.to_entity(mapped_cart_item)

    async def get_all(self) -> List[CartItem]:
        query = select(CartItemModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CartItemMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> CartItem | None:
        model = await self.db_session.get(CartItemModel, id)

        if model is None:
            return None

        return CartItemMapper.to_entity(model)

    async def get_by_cart_id(self, cart_id: uuid.UUID) -> List[CartItem]:
        query = select(CartItemModel).where(CartItemModel.cart_id == cart_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CartItemMapper.to_entity(model) for model in models]

    async def update_by_id(self, cart_item: CartItem) -> CartItem | None:
        model = CartItemMapper.to_model(cart_item)
        db_cart_item = await self.db_session.merge(model)

        if db_cart_item is None:
            return None

        await self.db_session.flush()

        return CartItemMapper.to_entity(db_cart_item)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(CartItemModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
