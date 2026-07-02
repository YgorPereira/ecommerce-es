from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.inventories.entity import Inventory
from src.modules.inventories.mapper import InventoryMapper
from src.modules.inventories.models import InventoryModel


class InventoryRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, inventory: Inventory) -> Inventory:
        mapped_inventory = InventoryMapper.to_model(inventory)
        self.db_session.add(mapped_inventory)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_inventory)
        return InventoryMapper.to_entity(mapped_inventory)

    async def get_all(self) -> List[Inventory]:
        query = select(InventoryModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [InventoryMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Inventory | None:
        model = await self.db_session.get(InventoryModel, id)

        if model is None:
            return None

        return InventoryMapper.to_entity(model)

    async def get_by_product_id(self, product_id: uuid.UUID) -> Inventory | None:
        query = select(InventoryModel).where(InventoryModel.product_id == product_id)
        model = await self.db_session.scalar(query)

        if model is None:
            return None

        return InventoryMapper.to_entity(model)

    async def update_by_id(self, inventory: Inventory) -> Inventory | None:
        model = InventoryMapper.to_model(inventory)
        db_inventory = await self.db_session.merge(model)

        if db_inventory is None:
            return None

        await self.db_session.flush()

        return InventoryMapper.to_entity(db_inventory)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(InventoryModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
