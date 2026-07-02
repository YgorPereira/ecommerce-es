from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.addresses.entity import Address
from src.modules.addresses.mapper import AddressMapper
from src.modules.addresses.models import AddressModel


class AddressRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, address: Address) -> Address:
        mapped_address = AddressMapper.to_model(address)
        self.db_session.add(mapped_address)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_address)
        return AddressMapper.to_entity(mapped_address)

    async def get_all(self) -> List[Address]:
        query = select(AddressModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [AddressMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Address | None:
        model = await self.db_session.get(AddressModel, id)

        if model is None:
            return None

        return AddressMapper.to_entity(model)

    async def get_by_user_id(self, user_id: uuid.UUID) -> List[Address]:
        query = select(AddressModel).where(AddressModel.user_id == user_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [AddressMapper.to_entity(model) for model in models]

    async def update_by_id(self, address: Address) -> Address | None:
        model = AddressMapper.to_model(address)
        db_address = await self.db_session.merge(model)

        if db_address is None:
            return None

        await self.db_session.flush()

        return AddressMapper.to_entity(db_address)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(AddressModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
