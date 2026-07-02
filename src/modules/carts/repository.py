from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.carts.entity import Cart
from src.modules.carts.mapper import CartMapper
from src.modules.carts.models import CartModel


class CartRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, cart: Cart) -> Cart:
        mapped_cart = CartMapper.to_model(cart)
        self.db_session.add(mapped_cart)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_cart)
        return CartMapper.to_entity(mapped_cart)

    async def get_all(self) -> List[Cart]:
        query = select(CartModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CartMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Cart | None:
        model = await self.db_session.get(CartModel, id)

        if model is None:
            return None

        return CartMapper.to_entity(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[Cart]:
        query = select(CartModel).where(CartModel.user_id == user_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CartMapper.to_entity(model) for model in models]

    async def update_by_id(self, cart: Cart) -> Cart | None:
        model = CartMapper.to_model(cart)
        db_cart = await self.db_session.merge(model)

        if db_cart is None:
            return None

        await self.db_session.flush()

        return CartMapper.to_entity(db_cart)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(CartModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
