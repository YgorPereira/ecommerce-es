import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.main import app
from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.router import get_cart_item_service
from src.modules.carts.entity import Cart
from src.modules.carts.exceptions import CartNotFoundException, EmptyCartException
from src.modules.carts.router import get_cart_service, get_checkout_service
from src.modules.inventories.exceptions import InsufficientStockException
from src.modules.orders.entity import Order


@pytest.fixture
def mock_cart_service():
    service = AsyncMock()
    app.dependency_overrides[get_cart_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_cart_service, None)


@pytest.fixture
def mock_cart_item_service():
    service = AsyncMock()
    app.dependency_overrides[get_cart_item_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_cart_item_service, None)


@pytest.fixture
def mock_checkout_service():
    service = AsyncMock()
    app.dependency_overrides[get_checkout_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_checkout_service, None)


@pytest.fixture
def cart():
    return Cart(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
    )


@pytest.mark.api
def test_create_cart(authenticated_client, mock_cart_service, cart):
    mock_cart_service.create_cart.return_value = cart

    response = authenticated_client.post(
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
def test_create_cart_without_coupon(authenticated_client, mock_cart_service, cart):
    cart.coupon_id = None
    mock_cart_service.create_cart.return_value = cart

    response = authenticated_client.post("/carts", json={"user_id": str(cart.user_id)})

    assert response.status_code == 201
    assert response.json()["coupon_id"] is None


@pytest.mark.api
def test_get_cart_by_id(authenticated_client, mock_cart_service, cart, user):
    cart.user_id = user.id
    mock_cart_service.get_cart_by_id.return_value = cart

    response = authenticated_client.get(f"/carts/{cart.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(cart.id)



@pytest.mark.api
def test_get_cart_by_id_not_found(authenticated_client, mock_cart_service):
    mock_cart_service.get_cart_by_id.side_effect = CartNotFoundException()

    response = authenticated_client.get(f"/carts/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_carts_by_user_id(authenticated_client, mock_cart_service, cart, user):
    cart.user_id = user.id
    mock_cart_service.get_carts_by_user_id.return_value = [cart]

    response = authenticated_client.get(f"/carts/user/{user.id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["user_id"] == str(user.id)


@pytest.mark.api
def test_get_all_carts(admin_client, mock_cart_service, cart):
    mock_cart_service.get_all_carts.return_value = [cart, cart]

    response = admin_client.get("/carts")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.api
def test_get_all_carts_empty(admin_client, mock_cart_service):
    mock_cart_service.get_all_carts.return_value = []

    response = admin_client.get("/carts")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_cart(authenticated_client, mock_cart_service, cart, user):
    cart.user_id = user.id
    mock_cart_service.repository.get_by_id.return_value = cart  # ⬅️ auth check
    mock_cart_service.update_cart.return_value = cart

    response = authenticated_client.put(
        "/carts",
        json={"id": str(cart.id), "user_id": str(cart.user_id), "coupon_id": str(cart.coupon_id)},
    )

    assert response.status_code == 200
    assert response.json()["id"] == str(cart.id)


@pytest.mark.api
def test_update_cart_not_found(authenticated_client, mock_cart_service):
    mock_cart_service.repository.get_by_id.side_effect = CartNotFoundException()

    response = authenticated_client.put(
        "/carts",
        json={"id": str(uuid.uuid4()), "user_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404


@pytest.mark.api
def test_delete_cart(authenticated_client, mock_cart_service, cart, user):
    cart.user_id = user.id
    mock_cart_service.get_cart_by_id.return_value = cart
    mock_cart_service.delete_cart_by_id.return_value = True

    response = authenticated_client.delete(f"/carts/{cart.id}")

    assert response.status_code == 204
    mock_cart_service.delete_cart_by_id.assert_awaited_once_with(cart.id)


@pytest.mark.api
def test_delete_cart_not_found(authenticated_client, mock_cart_service):
    mock_cart_service.get_cart_by_id.side_effect = CartNotFoundException()

    response = authenticated_client.delete(f"/carts/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_cart_items(authenticated_client, mock_cart_service, mock_cart_item_service, cart):
    item = CartItem(
        id=uuid.uuid4(),
        cart_id=cart.id,
        product_id=uuid.uuid4(),
        quantity=3,
    )
    mock_cart_service.get_cart_by_id.return_value = cart
    mock_cart_item_service.get_cart_items_by_cart_id.return_value = [item]

    response = authenticated_client.get(f"/carts/{cart.id}/items")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["cart_id"] == str(cart.id)
    assert body[0]["quantity"] == 3


@pytest.mark.api
def test_get_cart_items_cart_not_found(
    authenticated_client, mock_cart_service, mock_cart_item_service
):
    mock_cart_service.get_cart_by_id.side_effect = CartNotFoundException()

    response = authenticated_client.get(f"/carts/{uuid.uuid4()}/items")

    assert response.status_code == 404
    mock_cart_item_service.get_cart_items_by_cart_id.assert_not_awaited()


@pytest.mark.api
def test_checkout(authenticated_client, mock_checkout_service, cart, user):
    cart.user_id = user.id
    mock_checkout_service.cart_repository.get_by_id.return_value = cart

    order = Order(
        user_id=cart.user_id, address_id=uuid.uuid4(), total_amount=200.0,
        status="pending", created_at=datetime.now(timezone.utc), id=uuid.uuid4(),
    )
    mock_checkout_service.checkout.return_value = order

    response = authenticated_client.post(
        f"/carts/{cart.id}/checkout", json={"address_id": str(order.address_id)},
    )

    assert response.status_code == 201
    mock_checkout_service.checkout.assert_awaited_once_with(cart.id, order.address_id)


@pytest.mark.api
def test_checkout_empty_cart(authenticated_client, mock_checkout_service, cart, user):
    cart.user_id = user.id
    mock_checkout_service.cart_repository.get_by_id.return_value = cart
    mock_checkout_service.checkout.side_effect = EmptyCartException()

    response = authenticated_client.post(
        f"/carts/{cart.id}/checkout", json={"address_id": str(uuid.uuid4())},
    )

    assert response.status_code == 400


@pytest.mark.api
def test_checkout_insufficient_stock(authenticated_client, mock_checkout_service, cart, user):
    cart.user_id = user.id
    mock_checkout_service.cart_repository.get_by_id.return_value = cart
    mock_checkout_service.checkout.side_effect = InsufficientStockException()

    response = authenticated_client.post(
        f"/carts/{cart.id}/checkout", json={"address_id": str(uuid.uuid4())},
    )

    assert response.status_code == 409


@pytest.mark.api
def test_checkout_cart_not_found(authenticated_client, mock_checkout_service, cart, user):
    cart.user_id = user.id
    mock_checkout_service.cart_repository.get_by_id.return_value = cart
    mock_checkout_service.checkout.side_effect = CartNotFoundException()

    response = authenticated_client.post(
        f"/carts/{cart.id}/checkout", json={"address_id": str(uuid.uuid4())},
    )

    assert response.status_code == 404
