import uuid
from unittest.mock import AsyncMock

import pytest

from src.main import app
from src.modules.order_items.entity import OrderItem
from src.modules.order_items.exceptions import OrderItemNotFoundException
from src.modules.order_items.router import get_order_item_service


@pytest.fixture
def mock_order_item_service():
    service = AsyncMock()
    app.dependency_overrides[get_order_item_service] = lambda: service
    yield service
    app.dependency_overrides.pop(get_order_item_service, None)


@pytest.fixture
def order_item():
    return OrderItem(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=2,
        price=99.9,
    )


def _payload(order_item):
    return {
        "order_id": str(order_item.order_id),
        "product_id": str(order_item.product_id),
        "quantity": order_item.quantity,
        "price": order_item.price,
    }


@pytest.mark.api
def test_create_order_item(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.create_order_item.return_value = order_item

    response = admin_client.post("/order_items", json=_payload(order_item))

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(order_item.id)
    assert body["order_id"] == str(order_item.order_id)
    assert body["price"] == order_item.price

    mock_order_item_service.create_order_item.assert_awaited_once()


@pytest.mark.api
def test_create_order_item_invalid_quantity(admin_client, order_item):
    payload = _payload(order_item)
    payload["quantity"] = 0

    response = admin_client.post("/order_items", json=payload)

    assert response.status_code == 422


@pytest.mark.api
def test_get_order_item_by_id(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.get_order_item_by_id.return_value = order_item

    response = admin_client.get(f"/order_items/{order_item.id}")

    assert response.status_code == 200
    assert response.json()["id"] == str(order_item.id)


@pytest.mark.api
def test_get_order_item_by_id_not_found(admin_client, mock_order_item_service):
    mock_order_item_service.get_order_item_by_id.side_effect = (
        OrderItemNotFoundException()
    )

    response = admin_client.get(f"/order_items/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_order_items_by_order_id(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.get_order_items_by_order_id.return_value = [order_item]

    response = admin_client.get(f"/order_items/order/{order_item.order_id}")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["order_id"] == str(order_item.order_id)


@pytest.mark.api
def test_get_all_order_items(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.get_all_order_items.return_value = [order_item, order_item]

    response = admin_client.get("/order_items")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2


@pytest.mark.api
def test_get_all_order_items_empty(admin_client, mock_order_item_service):
    mock_order_item_service.get_all_order_items.return_value = []

    response = admin_client.get("/order_items")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_update_order_item(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.update_order_item.return_value = order_item

    payload = _payload(order_item)
    payload["id"] = str(order_item.id)

    response = admin_client.put("/order_items", json=payload)

    assert response.status_code == 200
    assert response.json()["id"] == str(order_item.id)


@pytest.mark.api
def test_update_order_item_not_found(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.update_order_item.side_effect = OrderItemNotFoundException()

    payload = _payload(order_item)
    payload["id"] = str(uuid.uuid4())

    response = admin_client.put("/order_items", json=payload)

    assert response.status_code == 404


@pytest.mark.api
def test_delete_order_item(admin_client, mock_order_item_service, order_item):
    mock_order_item_service.delete_order_item_by_id.return_value = True

    response = admin_client.delete(f"/order_items/{order_item.id}")

    assert response.status_code == 204
    mock_order_item_service.delete_order_item_by_id.assert_awaited_once_with(
        order_item.id
    )


@pytest.mark.api
def test_delete_order_item_not_found(admin_client, mock_order_item_service):
    mock_order_item_service.delete_order_item_by_id.side_effect = (
        OrderItemNotFoundException()
    )

    response = admin_client.delete(f"/order_items/{uuid.uuid4()}")

    assert response.status_code == 404
