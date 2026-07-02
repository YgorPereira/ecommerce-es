from datetime import datetime, timezone
from typing import List
import uuid

from sqlalchemy import select, update
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

    async def decrement(self, product_id: uuid.UUID, quantity: int) -> bool:
        """Baixa o estoque de forma atômica.

        Usa um UPDATE condicional (``quantity >= :quantity``): o próprio banco
        garante que dois requests concorrentes não deixem o estoque negativo,
        pois cada UPDATE é atômico. Retorna ``True`` se a baixa ocorreu (havia
        estoque) e ``False`` caso contrário (sem estoque ou produto inexistente).
        """
        stmt = (
            update(InventoryModel)
            .where(
                InventoryModel.product_id == product_id,
                InventoryModel.quantity >= quantity,
            )
            .values(
                quantity=InventoryModel.quantity - quantity,
                updated_at=datetime.now(timezone.utc),
            )
        )
        result = await self.db_session.execute(stmt)
        return result.rowcount == 1

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
