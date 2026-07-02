import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.main import app
from src.modules.inventories.entity import Inventory
from src.modules.inventories.exceptions import (
    InsufficientStockException,
    InventoryAlreadyExistsException,
    InventoryNotFoundException,
)
from src.modules.inventories.router import get_inventory_service


@pytest.fixture
def mock_inventory_service():
    service = AsyncMock()
    app.dependency_overrides[get_inventory_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_inventory_service, None)


@pytest.fixture
def inventory():
    return Inventory(
        id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=50,
        updated_at=datetime.now(timezone.utc),
    )


@pytest.mark.api
def test_create_inventory(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.create_inventory.return_value = inventory

    response = admin_client.post(
        "/inventories",
        json={
            "product_id": str(inventory.product_id),
            "quantity": inventory.quantity,
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(inventory.id)
    assert body["product_id"] == str(inventory.product_id)
    assert body["quantity"] == inventory.quantity

    mock_inventory_service.create_inventory.assert_awaited_once()


@pytest.mark.api
def test_create_inventory_already_exists(admin_client, mock_inventory_service):
    mock_inventory_service.create_inventory.side_effect = (
        InventoryAlreadyExistsException()
    )

    response = admin_client.post(
        "/inventories",
        json={"product_id": str(uuid.uuid4()), "quantity": 10},
    )

    assert response.status_code == 409


@pytest.mark.api
def test_create_inventory_negative_quantity(admin_client):
    response = admin_client.post(
        "/inventories",
        json={"product_id": str(uuid.uuid4()), "quantity": -5},
    )

    assert response.status_code == 422


@pytest.mark.api
def test_get_inventory_by_id(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.get_inventory_by_id.return_value = inventory

    response = admin_client.get(f"/inventories/{inventory.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(inventory.id)


@pytest.mark.api
def test_get_inventory_by_id_not_found(admin_client, mock_inventory_service):
    mock_inventory_service.get_inventory_by_id.side_effect = (
        InventoryNotFoundException()
    )

    response = admin_client.get(f"/inventories/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_inventory_by_product_id(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.get_inventory_by_product_id.return_value = inventory

    response = admin_client.get(f"/inventories/product/{inventory.product_id}")

    assert response.status_code == 200
    assert response.json()["product_id"] == str(inventory.product_id)


@pytest.mark.api
def test_get_inventory_by_product_id_not_found(admin_client, mock_inventory_service):
    mock_inventory_service.get_inventory_by_product_id.side_effect = (
        InventoryNotFoundException()
    )

    response = admin_client.get(f"/inventories/product/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_all_inventories(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.get_all_inventories.return_value = [inventory, inventory]

    response = admin_client.get("/inventories")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_inventories_empty(admin_client, mock_inventory_service):
    mock_inventory_service.get_all_inventories.return_value = []

    response = admin_client.get("/inventories")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_reserve_stock(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.reserve_stock.return_value = inventory

    response = admin_client.post(
        f"/inventories/product/{inventory.product_id}/reserve",
        json={"quantity": 1},
    )

    assert response.status_code == 200
    assert response.json()["product_id"] == str(inventory.product_id)
    mock_inventory_service.reserve_stock.assert_awaited_once_with(
        inventory.product_id, 1
    )


@pytest.mark.api
def test_reserve_stock_insufficient(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.reserve_stock.side_effect = InsufficientStockException()

    response = admin_client.post(
        f"/inventories/product/{inventory.product_id}/reserve",
        json={"quantity": 99},
    )

    assert response.status_code == 409


@pytest.mark.api
def test_reserve_stock_invalid_quantity(admin_client, inventory):
    response = admin_client.post(
        f"/inventories/product/{inventory.product_id}/reserve",
        json={"quantity": 0},
    )

    assert response.status_code == 422


@pytest.mark.api
def test_update_inventory(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.update_inventory.return_value = inventory

    response = admin_client.put(
        "/inventories",
        json={
            "id": str(inventory.id),
            "product_id": str(inventory.product_id),
            "quantity": 30,
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(inventory.id)


@pytest.mark.api
def test_update_inventory_not_found(admin_client, mock_inventory_service):
    mock_inventory_service.update_inventory.side_effect = InventoryNotFoundException()

    response = admin_client.put(
        "/inventories",
        json={
            "id": str(uuid.uuid4()),
            "product_id": str(uuid.uuid4()),
            "quantity": 30,
        },
    )

    assert response.status_code == 404


@pytest.mark.api
def test_delete_inventory(admin_client, mock_inventory_service, inventory):
    mock_inventory_service.delete_inventory_by_id.return_value = True

    response = admin_client.delete(f"/inventories/{inventory.id}")

    assert response.status_code == 204
    mock_inventory_service.delete_inventory_by_id.assert_awaited_once_with(inventory.id)


@pytest.mark.api
def test_delete_inventory_not_found(admin_client, mock_inventory_service):
    mock_inventory_service.delete_inventory_by_id.side_effect = (
        InventoryNotFoundException()
    )

    response = admin_client.delete(f"/inventories/{uuid.uuid4()}")

    assert response.status_code == 404
