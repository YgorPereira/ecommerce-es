from datetime import datetime, timezone
from typing import List
import uuid

from src.modules.inventories.entity import Inventory
from src.modules.inventories.exceptions import (
    InsufficientStockException,
    InventoryAlreadyExistsException,
    InventoryNotFoundException,
)
from src.modules.inventories.repository import InventoryRepository
from src.modules.inventories.schemas import (
    CreateInventorySchema,
    UpdateInventorySchema,
)


class InventoryService:
    def __init__(self, repository: InventoryRepository):
        self.repository = repository

    async def create_inventory(self, inventory: CreateInventorySchema) -> Inventory:
        db_item = await self.repository.get_by_product_id(inventory.product_id)

        if db_item is not None:
            raise InventoryAlreadyExistsException()

        return await self.repository.create(
            Inventory(
                product_id=inventory.product_id,
                quantity=inventory.quantity,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def get_all_inventories(self) -> List[Inventory]:
        return await self.repository.get_all()

    async def get_inventory_by_id(self, id: uuid.UUID) -> Inventory:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise InventoryNotFoundException()

        return db_item

    async def get_inventory_by_product_id(self, product_id: uuid.UUID) -> Inventory:
        db_item = await self.repository.get_by_product_id(product_id)

        if db_item is None:
            raise InventoryNotFoundException()

        return db_item

    async def update_inventory(
        self, inventory: UpdateInventorySchema
    ) -> Inventory | None:
        db_item = await self.repository.get_by_id(inventory.id)

        if db_item is None:
            raise InventoryNotFoundException()

        return await self.repository.update_by_id(
            Inventory(
                id=inventory.id,
                product_id=inventory.product_id,
                quantity=inventory.quantity,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def reserve_stock(self, product_id: uuid.UUID, quantity: int) -> Inventory:
        """Reserva (baixa) estoque de forma atômica e à prova de concorrência.

        Se dois usuários tentarem reservar a última unidade ao mesmo tempo,
        apenas um consegue: o outro recebe ``InsufficientStockException``.
        """
        reserved = await self.repository.decrement(product_id, quantity)

        if not reserved:
            existing = await self.repository.get_by_product_id(product_id)

            if existing is None:
                raise InventoryNotFoundException()

            raise InsufficientStockException()

        reserved_item = await self.repository.get_by_product_id(product_id)

        if reserved_item is None:
            raise InventoryNotFoundException()

        return reserved_item

    async def delete_inventory_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise InventoryNotFoundException()

        return await self.repository.delete_by_id(id)
