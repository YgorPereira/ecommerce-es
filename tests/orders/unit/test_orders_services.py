import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from datetime import timedelta

from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import (
    CouponExpiredException,
    CouponNotFoundException,
    CouponUsageLimitReachedException,
)
from src.modules.order_items.entity import OrderItem
from src.modules.orders.entity import Order
from src.modules.orders.exceptions import (
    OrderAlreadyPaidException,
    OrderNotFoundException,
)
from src.modules.orders.schemas import CreateOrderSchema, UpdateOrderSchema
from src.modules.orders.services import (
    DEFAULT_ORDER_STATUS,
    PAID_ORDER_STATUS,
    OrderService,
)


async def _echo(entity):
    return entity


def _order(coupon_id=None):
    return Order(
        user_id=uuid.uuid4(),
        address_id=uuid.uuid4(),
        coupon_id=coupon_id,
        total_amount=0.0,
        status="pending",
        created_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


def _items(order_id):
    return [
        OrderItem(order_id=order_id, product_id=uuid.uuid4(), quantity=2, price=100.0),
        OrderItem(order_id=order_id, product_id=uuid.uuid4(), quantity=1, price=50.0),
    ]


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def mock_order_item_repository():
    return AsyncMock()


@pytest.fixture
def mock_coupon_repository():
    return AsyncMock()


@pytest.fixture
def order_service(mock_repository, mock_order_item_repository, mock_coupon_repository):
    return OrderService(
        repository=mock_repository,
        order_item_repository=mock_order_item_repository,
        coupon_repository=mock_coupon_repository,
    )


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


@pytest.mark.unit()
async def test_calculate_order_total_no_coupon(
    order_service, mock_repository, mock_order_item_repository
):
    order = _order(coupon_id=None)
    mock_repository.get_by_id.return_value = order
    mock_order_item_repository.get_by_order_id.return_value = _items(order.id)
    mock_repository.update_by_id.side_effect = _echo

    result = await order_service.calculate_order_total(order.id)

    # 2*100 + 1*50 = 250
    assert result.total_amount == 250.0


@pytest.mark.unit()
async def test_calculate_order_total_with_valid_coupon(
    order_service, mock_repository, mock_order_item_repository, mock_coupon_repository
):
    order = _order(coupon_id=uuid.uuid4())
    mock_repository.get_by_id.return_value = order
    mock_order_item_repository.get_by_order_id.return_value = _items(order.id)
    mock_coupon_repository.get_by_id.return_value = Coupon(
        discount_percentage=10.0,
        discount_amount=5.0,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        usage_limit=10,
        id=order.coupon_id,
    )
    mock_repository.update_by_id.side_effect = _echo

    result = await order_service.calculate_order_total(order.id)

    # 250 - 10% = 225 ; 225 - 5 = 220
    assert result.total_amount == 220.0


@pytest.mark.unit()
async def test_calculate_order_total_expired_coupon(
    order_service, mock_repository, mock_order_item_repository, mock_coupon_repository
):
    order = _order(coupon_id=uuid.uuid4())
    mock_repository.get_by_id.return_value = order
    mock_order_item_repository.get_by_order_id.return_value = _items(order.id)
    mock_coupon_repository.get_by_id.return_value = Coupon(
        discount_percentage=10.0,
        discount_amount=0.0,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        usage_limit=10,
        id=order.coupon_id,
    )

    with pytest.raises(CouponExpiredException):
        await order_service.calculate_order_total(order.id)

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_calculate_order_total_usage_limit_reached(
    order_service, mock_repository, mock_order_item_repository, mock_coupon_repository
):
    order = _order(coupon_id=uuid.uuid4())
    mock_repository.get_by_id.return_value = order
    mock_order_item_repository.get_by_order_id.return_value = _items(order.id)
    mock_coupon_repository.get_by_id.return_value = Coupon(
        discount_percentage=10.0,
        discount_amount=0.0,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        usage_limit=0,
        id=order.coupon_id,
    )

    with pytest.raises(CouponUsageLimitReachedException):
        await order_service.calculate_order_total(order.id)


@pytest.mark.unit()
async def test_calculate_order_total_coupon_not_found(
    order_service, mock_repository, mock_order_item_repository, mock_coupon_repository
):
    order = _order(coupon_id=uuid.uuid4())
    mock_repository.get_by_id.return_value = order
    mock_order_item_repository.get_by_order_id.return_value = _items(order.id)
    mock_coupon_repository.get_by_id.return_value = None

    with pytest.raises(CouponNotFoundException):
        await order_service.calculate_order_total(order.id)


@pytest.mark.unit()
async def test_calculate_order_total_order_not_found(order_service, mock_repository):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await order_service.calculate_order_total(uuid.uuid4())


@pytest.mark.unit()
async def test_update_paid_order_is_blocked(
    order_service, mock_repository, update_schema
):
    paid_order = _order()
    paid_order.status = PAID_ORDER_STATUS
    mock_repository.get_by_id.return_value = paid_order

    with pytest.raises(OrderAlreadyPaidException):
        await order_service.update_order(update_schema)

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_paid_order_is_blocked(order_service, mock_repository):
    paid_order = _order()
    paid_order.status = PAID_ORDER_STATUS
    mock_repository.get_by_id.return_value = paid_order

    with pytest.raises(OrderAlreadyPaidException):
        await order_service.delete_order_by_id(paid_order.id)

    mock_repository.delete_by_id.assert_not_called()
