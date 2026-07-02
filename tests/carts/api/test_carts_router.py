import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.router import get_cart_item_service
from src.modules.carts.entity import Cart
from src.modules.carts.exceptions import CartNotFoundException
from src.modules.carts.router import get_cart_service


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def mock_cart_service():
    service = AsyncMock()
    app.dependency_overrides[get_cart_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def mock_cart_item_service():
    service = AsyncMock()
    app.dependency_overrides[get_cart_item_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def cart():
    return Cart(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.api
def test_create_cart(client, mock_cart_service, cart):
    mock_cart_service.create_cart.return_value = cart

    response = client.post(
        "/carts",
        json={
            "user_id": str(cart.user_id),
            "coupon_id": str(cart.coupon_id),
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(cart.id)
    assert body["user_id"] == str(cart.user_id)

    mock_cart_service.create_cart.assert_awaited_once()


@pytest.mark.api
def test_create_cart_without_coupon(client, mock_cart_service, cart):
    cart.coupon_id = None
    mock_cart_service.create_cart.return_value = cart

    response = client.post("/carts", json={"user_id": str(cart.user_id)})

    assert response.status_code == 201
    assert response.json()["coupon_id"] is None


@pytest.mark.api
def test_get_cart_by_id(client, mock_cart_service, cart):
    mock_cart_service.get_cart_by_id.return_value = cart

    response = client.get(f"/carts/{cart.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(cart.id)


@pytest.mark.api
def test_get_cart_by_id_not_found(client, mock_cart_service):
    mock_cart_service.get_cart_by_id.side_effect = CartNotFoundException()

    response = client.get(f"/carts/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_carts_by_user_id(client, mock_cart_service, cart):
    mock_cart_service.get_carts_by_user_id.return_value = [cart]

    response = client.get(f"/carts/user/{cart.user_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["user_id"] == str(cart.user_id)


@pytest.mark.api
def test_get_all_carts(client, mock_cart_service, cart):
    mock_cart_service.get_all_carts.return_value = [cart, cart]

    response = client.get("/carts")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_carts_empty(client, mock_cart_service):
    mock_cart_service.get_all_carts.return_value = []

    response = client.get("/carts")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_cart(client, mock_cart_service, cart):
    mock_cart_service.update_cart.return_value = cart

    response = client.put(
        "/carts",
        json={
            "id": str(cart.id),
            "user_id": str(cart.user_id),
            "coupon_id": str(cart.coupon_id),
        },
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(cart.id)


@pytest.mark.api
def test_update_cart_not_found(client, mock_cart_service):
    mock_cart_service.update_cart.side_effect = CartNotFoundException()

    response = client.put(
        "/carts",
        json={"id": str(uuid.uuid4()), "user_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404


@pytest.mark.api
def test_delete_cart(client, mock_cart_service, cart):
    mock_cart_service.delete_cart_by_id.return_value = True

    response = client.delete(f"/carts/{cart.id}")

    assert response.status_code == 204
    mock_cart_service.delete_cart_by_id.assert_awaited_once_with(cart.id)


@pytest.mark.api
def test_delete_cart_not_found(client, mock_cart_service):
    mock_cart_service.delete_cart_by_id.side_effect = CartNotFoundException()

    response = client.delete(f"/carts/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_cart_items(client, mock_cart_service, mock_cart_item_service, cart):
    item = CartItem(
        id=uuid.uuid4(),
        cart_id=cart.id,
        product_id=uuid.uuid4(),
        quantity=3,
    )
    mock_cart_service.get_cart_by_id.return_value = cart
    mock_cart_item_service.get_cart_items_by_cart_id.return_value = [item]

    response = client.get(f"/carts/{cart.id}/items")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["cart_id"] == str(cart.id)
    assert body[0]["quantity"] == 3


@pytest.mark.api
def test_get_cart_items_cart_not_found(
    client, mock_cart_service, mock_cart_item_service
):
    mock_cart_service.get_cart_by_id.side_effect = CartNotFoundException()

    response = client.get(f"/carts/{uuid.uuid4()}/items")

    assert response.status_code == 404
    mock_cart_item_service.get_cart_items_by_cart_id.assert_not_awaited()
