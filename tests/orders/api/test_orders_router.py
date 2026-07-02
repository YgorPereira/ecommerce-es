import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.main import app
from src.modules.orders.entity import Order
from src.modules.orders.exceptions import OrderNotFoundException
from src.modules.orders.router import get_order_service


@pytest.fixture
def mock_order_service():
    service = AsyncMock()
    app.dependency_overrides[get_order_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_order_service, None)


@pytest.fixture
def order():
    return Order(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        address_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
        total_amount=250.0,
        status="pending",
        created_at=datetime.now(timezone.utc),
    )


def _payload(order):
    return {
        "user_id": str(order.user_id),
        "address_id": str(order.address_id),
        "coupon_id": str(order.coupon_id),
        "total_amount": order.total_amount,
    }


@pytest.mark.api
def test_create_order(authenticated_client, mock_order_service, order):
    mock_order_service.create_order.return_value = order

    response = authenticated_client.post("/orders", json=_payload(order))

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(order.id)
    assert body["status"] == "pending"
    assert body["total_amount"] == order.total_amount

    mock_order_service.create_order.assert_awaited_once()


@pytest.mark.api
def test_create_order_negative_total(authenticated_client, order):
    payload = _payload(order)
    payload["total_amount"] = -10.0

    response = authenticated_client.post("/orders", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_order_by_id(authenticated_client, mock_order_service, order, user):
    order.user_id = user.id
    mock_order_service.get_order_by_id.return_value = order

    response = authenticated_client.get(f"/orders/{order.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(order.id)


@pytest.mark.api
def test_get_order_by_id_not_found(authenticated_client, mock_order_service):
    mock_order_service.get_order_by_id.side_effect = OrderNotFoundException()

    response = authenticated_client.get(f"/orders/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_calculate_order_total(authenticated_client, mock_order_service, order):
    order.total_amount = 220.0
    mock_order_service.calculate_order_total.return_value = order

    response = authenticated_client.post(f"/orders/{order.id}/calculate-total")

    assert response.status_code == 200
    assert response.json()["total_amount"] == 220.0
    mock_order_service.calculate_order_total.assert_awaited_once_with(order.id)


@pytest.mark.api
def test_calculate_order_total_not_found(authenticated_client, mock_order_service):
    mock_order_service.calculate_order_total.side_effect = OrderNotFoundException()

    response = authenticated_client.post(f"/orders/{uuid.uuid4()}/calculate-total")

    assert response.status_code == 404


@pytest.mark.api
def test_get_orders_by_user_id(authenticated_client, mock_order_service, order, user):
    order.user_id = user.id
    mock_order_service.get_orders_by_user_id.return_value = [order]

    response = authenticated_client.get(f"/orders/user/{user.id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["user_id"] == str(user.id)


@pytest.mark.api
def test_get_all_orders(admin_client, mock_order_service, order):
    mock_order_service.get_all_orders.return_value = [order, order]

    response = admin_client.get("/orders")

    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.api
def test_get_all_orders_empty(admin_client, mock_order_service):
    mock_order_service.get_all_orders.return_value = []

    response = admin_client.get("/orders")

    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.api
def test_update_order(admin_client, mock_order_service, order):
    order.status = "paid"
    mock_order_service.update_order.return_value = order

    payload = _payload(order)
    payload["id"] = str(order.id)
    payload["status"] = "paid"

    response = admin_client.put("/orders", json=payload)

    assert response.status_code == 200
    assert response.json()["status"] == "paid"


@pytest.mark.api
def test_update_order_not_found(admin_client, mock_order_service, order):
    mock_order_service.update_order.side_effect = OrderNotFoundException()

    payload = _payload(order)
    payload["id"] = str(uuid.uuid4())
    payload["status"] = "paid"

    response = admin_client.put("/orders", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_delete_order(authenticated_client, mock_order_service, order):
    mock_order_service.delete_order_by_id.return_value = True

    response = authenticated_client.delete(f"/orders/{order.id}")

    assert response.status_code == 204
    mock_order_service.delete_order_by_id.assert_awaited_once_with(order.id)


@pytest.mark.api
def test_delete_order_not_found(authenticated_client, mock_order_service):
    mock_order_service.delete_order_by_id.side_effect = OrderNotFoundException()

    response = authenticated_client.delete(f"/orders/{uuid.uuid4()}")

    assert response.status_code == 404
