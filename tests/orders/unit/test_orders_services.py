import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.orders.entity import Order
from src.modules.orders.exceptions import OrderNotFoundException
from src.modules.orders.schemas import CreateOrderSchema, UpdateOrderSchema
from src.modules.orders.services import DEFAULT_ORDER_STATUS, OrderService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def order_service(mock_repository):
    return OrderService(repository=mock_repository)


@pytest.fixture
def order():
    return Order(
        user_id=uuid.uuid4(),
        address_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
        total_amount=250.0,
        status="pending",
        created_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(order):
    return CreateOrderSchema(
        user_id=order.user_id,
        address_id=order.address_id,
        coupon_id=order.coupon_id,
        total_amount=order.total_amount,
    )


@pytest.fixture
def update_schema(order):
    return UpdateOrderSchema(
        id=order.id,
        user_id=order.user_id,
        address_id=order.address_id,
        coupon_id=order.coupon_id,
        total_amount=order.total_amount,
        status="paid",
    )


@pytest.mark.unit()
async def test_create_order(order_service, mock_repository, create_schema, order):
    mock_repository.create.return_value = order

    created = await order_service.create_order(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Order)
    assert created.total_amount == order.total_amount


@pytest.mark.unit()
async def test_create_order_defaults_status_and_created_at(
    order_service, mock_repository, create_schema
):
    async def echo(entity):
        return entity

    mock_repository.create.side_effect = echo

    created = await order_service.create_order(create_schema)

    assert created.status == DEFAULT_ORDER_STATUS
    assert created.created_at is not None


@pytest.mark.unit()
async def test_get_all_orders(order_service, mock_repository, order):
    mock_repository.get_all.return_value = [order, order]

    orders = await order_service.get_all_orders()

    mock_repository.get_all.assert_called_once()
    assert len(orders) == 2


@pytest.mark.unit()
async def test_get_order_by_id(order_service, mock_repository, order):
    mock_repository.get_by_id.return_value = order

    found = await order_service.get_order_by_id(order.id)

    mock_repository.get_by_id.assert_called_once_with(order.id)
    assert found.id == order.id


@pytest.mark.unit()
async def test_get_order_by_id_not_found(order_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(OrderNotFoundException):
        await order_service.get_order_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_orders_by_user_id(order_service, mock_repository, order):
    mock_repository.get_by_user_id.return_value = [order]

    orders = await order_service.get_orders_by_user_id(order.user_id)

    mock_repository.get_by_user_id.assert_called_once_with(order.user_id)
    assert len(orders) == 1
    assert orders[0].user_id == order.user_id


@pytest.mark.unit()
async def test_update_order_changes_status_preserves_created_at(
    order_service, mock_repository, order, update_schema
):
    mock_repository.get_by_id.return_value = order

    async def echo(entity):
        return entity

    mock_repository.update_by_id.side_effect = echo

    result = await order_service.update_order(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.status == "paid"
    assert result.created_at == order.created_at


@pytest.mark.unit()
async def test_update_order_not_found(order_service, mock_repository, update_schema):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await order_service.update_order(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_order_by_id(order_service, mock_repository, order):
    mock_repository.get_by_id.return_value = order
    mock_repository.delete_by_id.return_value = True

    is_deleted = await order_service.delete_order_by_id(order.id)

    mock_repository.get_by_id.assert_called_once_with(order.id)
    mock_repository.delete_by_id.assert_called_once_with(order.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_order_by_id_not_found(order_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await order_service.delete_order_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
