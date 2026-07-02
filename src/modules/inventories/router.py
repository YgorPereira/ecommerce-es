from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.modules.inventories.repository import InventoryRepository
from src.modules.inventories.schemas import (
    CreateInventorySchema,
    UpdateInventorySchema,
    InventoryResponseSchema,
    ReserveStockSchema,
)
from src.modules.inventories.services import InventoryService

inventory_router = APIRouter(
    prefix="/inventories",
    tags=["Inventories"],
)


def get_inventory_service(
    db: Session = Depends(get_db),
) -> InventoryService:
    repository = InventoryRepository(db)
    return InventoryService(repository)


@inventory_router.post(
    "",
    response_model=InventoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_inventory(
    inventory: CreateInventorySchema,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.create_inventory(inventory)


@inventory_router.get(
    "",
    response_model=List[InventoryResponseSchema],
)
async def get_all_inventories(
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.get_all_inventories()


@inventory_router.get(
    "/{inventory_id}",
    response_model=InventoryResponseSchema,
)
async def get_inventory_by_id(
    inventory_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.get_inventory_by_id(inventory_id)


@inventory_router.get(
    "/product/{product_id}",
    response_model=InventoryResponseSchema,
)
async def get_inventory_by_product_id(
    product_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.get_inventory_by_product_id(product_id)


@inventory_router.post(
    "/product/{product_id}/reserve",
    response_model=InventoryResponseSchema,
)
async def reserve_stock(
    product_id: UUID,
    reservation: ReserveStockSchema,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.reserve_stock(product_id, reservation.quantity)


@inventory_router.put(
    "",
    response_model=InventoryResponseSchema,
)
async def update_inventory(
    inventory: UpdateInventorySchema,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    return await service.update_inventory(inventory)


@inventory_router.delete(
    "/{inventory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_inventory(
    inventory_id: UUID,
    service: InventoryService = Depends(get_inventory_service),
    _: User = Depends(require_admin),
):
    await service.delete_inventory_by_id(inventory_id)
