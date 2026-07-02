import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.exceptions import CartItemNotFoundException
from src.modules.cart_items.router import get_cart_item_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_cart_item_service():
    service = AsyncMock()
    app.dependency_overrides[get_cart_item_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def cart_item():
    return CartItem(
        id=uuid.uuid4(),
        cart_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=2,
    )


def _payload(cart_item):
    return {
        "cart_id": str(cart_item.cart_id),
        "product_id": str(cart_item.product_id),
        "quantity": cart_item.quantity,
    }


@pytest.mark.api
def test_create_cart_item(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.create_cart_item.return_value = cart_item

    response = client.post("/cart_items", json=_payload(cart_item))

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(cart_item.id)
    assert body["cart_id"] == str(cart_item.cart_id)
    assert body["quantity"] == cart_item.quantity

    mock_cart_item_service.create_cart_item.assert_awaited_once()


@pytest.mark.api
def test_create_cart_item_invalid_quantity(client, cart_item):
    payload = _payload(cart_item)
    payload["quantity"] = 0

    response = client.post("/cart_items", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_cart_item_by_id(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.get_cart_item_by_id.return_value = cart_item

    response = client.get(f"/cart_items/{cart_item.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(cart_item.id)


@pytest.mark.api
def test_get_cart_item_by_id_not_found(client, mock_cart_item_service):
    mock_cart_item_service.get_cart_item_by_id.side_effect = CartItemNotFoundException()

    response = client.get(f"/cart_items/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_cart_items_by_cart_id(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.get_cart_items_by_cart_id.return_value = [cart_item]

    response = client.get(f"/cart_items/cart/{cart_item.cart_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["cart_id"] == str(cart_item.cart_id)


@pytest.mark.api
def test_get_all_cart_items(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.get_all_cart_items.return_value = [cart_item, cart_item]

    response = client.get("/cart_items")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_cart_items_empty(client, mock_cart_item_service):
    mock_cart_item_service.get_all_cart_items.return_value = []

    response = client.get("/cart_items")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_cart_item(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.update_cart_item.return_value = cart_item

    payload = _payload(cart_item)
    payload["id"] = str(cart_item.id)

    response = client.put("/cart_items", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == str(cart_item.id)


@pytest.mark.api
def test_update_cart_item_not_found(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.update_cart_item.side_effect = CartItemNotFoundException()

    payload = _payload(cart_item)
    payload["id"] = str(uuid.uuid4())

    response = client.put("/cart_items", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_delete_cart_item(client, mock_cart_item_service, cart_item):
    mock_cart_item_service.delete_cart_item_by_id.return_value = True

    response = client.delete(f"/cart_items/{cart_item.id}")

    assert response.status_code == 204
    mock_cart_item_service.delete_cart_item_by_id.assert_awaited_once_with(cart_item.id)


@pytest.mark.api
def test_delete_cart_item_not_found(client, mock_cart_item_service):
    mock_cart_item_service.delete_cart_item_by_id.side_effect = (
        CartItemNotFoundException()
    )

    response = client.delete(f"/cart_items/{uuid.uuid4()}")

    assert response.status_code == 404
