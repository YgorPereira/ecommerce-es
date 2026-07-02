import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.inventories.entity import Inventory
from src.modules.inventories.exceptions import (
    InventoryAlreadyExistsException,
    InventoryNotFoundException,
)
from src.modules.inventories.schemas import (
    CreateInventorySchema,
    UpdateInventorySchema,
)
from src.modules.inventories.services import InventoryService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def inventory_service(mock_repository):
    return InventoryService(repository=mock_repository)


@pytest.fixture
def inventory():
    return Inventory(
        product_id=uuid.uuid4(),
        quantity=50,
        updated_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(inventory):
    return CreateInventorySchema(
        product_id=inventory.product_id,
        quantity=inventory.quantity,
    )


@pytest.fixture
def update_schema(inventory):
    return UpdateInventorySchema(
        id=inventory.id,
        product_id=inventory.product_id,
        quantity=30,
    )


@pytest.mark.unit()
async def test_create_inventory(
    inventory_service, mock_repository, create_schema, inventory
):
    mock_repository.get_by_product_id.return_value = None
    mock_repository.create.return_value = inventory

    created = await inventory_service.create_inventory(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Inventory)
    assert created.quantity == inventory.quantity


@pytest.mark.unit()
async def test_create_inventory_already_exists(
    inventory_service, mock_repository, create_schema, inventory
):
    mock_repository.get_by_product_id.return_value = inventory

    with pytest.raises(InventoryAlreadyExistsException):
        await inventory_service.create_inventory(create_schema)

    mock_repository.get_by_product_id.assert_called_once_with(create_schema.product_id)
    mock_repository.create.assert_not_called()


@pytest.mark.unit()
async def test_get_all_inventories(inventory_service, mock_repository, inventory):
    mock_repository.get_all.return_value = [inventory, inventory]

    inventories = await inventory_service.get_all_inventories()

    mock_repository.get_all.assert_called_once()
    assert len(inventories) == 2


@pytest.mark.unit()
async def test_get_all_inventories_empty(inventory_service, mock_repository):
    mock_repository.get_all.return_value = []

    inventories = await inventory_service.get_all_inventories()

    mock_repository.get_all.assert_called_once()
    assert inventories == []


@pytest.mark.unit()
async def test_get_inventory_by_id(inventory_service, mock_repository, inventory):
    mock_repository.get_by_id.return_value = inventory

    found = await inventory_service.get_inventory_by_id(inventory.id)

    mock_repository.get_by_id.assert_called_once_with(inventory.id)
    assert found.id == inventory.id


@pytest.mark.unit()
async def test_get_inventory_by_id_not_found(inventory_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(InventoryNotFoundException):
        await inventory_service.get_inventory_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_inventory_by_product_id(
    inventory_service, mock_repository, inventory
):
    mock_repository.get_by_product_id.return_value = inventory

    found = await inventory_service.get_inventory_by_product_id(inventory.product_id)

    mock_repository.get_by_product_id.assert_called_once_with(inventory.product_id)
    assert found.product_id == inventory.product_id


@pytest.mark.unit()
async def test_get_inventory_by_product_id_not_found(
    inventory_service, mock_repository
):
    mock_repository.get_by_product_id.return_value = None

    with pytest.raises(InventoryNotFoundException):
        await inventory_service.get_inventory_by_product_id(uuid.uuid4())


@pytest.mark.unit()
async def test_update_inventory(
    inventory_service, mock_repository, inventory, update_schema
):
    updated = Inventory(
        product_id=update_schema.product_id,
        quantity=update_schema.quantity,
        updated_at=datetime.now(timezone.utc),
        id=inventory.id,
    )
    mock_repository.get_by_id.return_value = inventory
    mock_repository.update_by_id.return_value = updated

    result = await inventory_service.update_inventory(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.quantity == update_schema.quantity


@pytest.mark.unit()
async def test_update_inventory_not_found(
    inventory_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(InventoryNotFoundException):
        await inventory_service.update_inventory(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_inventory_by_id(inventory_service, mock_repository, inventory):
    mock_repository.get_by_id.return_value = inventory
    mock_repository.delete_by_id.return_value = True

    is_deleted = await inventory_service.delete_inventory_by_id(inventory.id)

    mock_repository.get_by_id.assert_called_once_with(inventory.id)
    mock_repository.delete_by_id.assert_called_once_with(inventory.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_inventory_by_id_not_found(inventory_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(InventoryNotFoundException):
        await inventory_service.delete_inventory_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
