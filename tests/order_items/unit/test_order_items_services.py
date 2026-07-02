import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.order_items.entity import OrderItem
from src.modules.order_items.exceptions import OrderItemNotFoundException
from src.modules.order_items.schemas import (
    CreateOrderItemSchema,
    UpdateOrderItemSchema,
)
from src.modules.order_items.services import OrderItemService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def order_item_service(mock_repository):
    return OrderItemService(repository=mock_repository)


@pytest.fixture
def order_item():
    return OrderItem(
        order_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=2,
        price=99.9,
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(order_item):
    return CreateOrderItemSchema(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        price=order_item.price,
    )


@pytest.fixture
def update_schema(order_item):
    return UpdateOrderItemSchema(
        id=order_item.id,
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=5,
        price=120.0,
    )


@pytest.mark.unit()
async def test_create_order_item(
    order_item_service, mock_repository, create_schema, order_item
):
    mock_repository.create.return_value = order_item

    created = await order_item_service.create_order_item(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, OrderItem)
    assert created.price == order_item.price


@pytest.mark.unit()
async def test_get_all_order_items(order_item_service, mock_repository, order_item):
    mock_repository.get_all.return_value = [order_item, order_item]

    items = await order_item_service.get_all_order_items()

    mock_repository.get_all.assert_called_once()
    assert len(items) == 2


@pytest.mark.unit()
async def test_get_all_order_items_empty(order_item_service, mock_repository):
    mock_repository.get_all.return_value = []

    items = await order_item_service.get_all_order_items()

    mock_repository.get_all.assert_called_once()
    assert items == []


@pytest.mark.unit()
async def test_get_order_item_by_id(order_item_service, mock_repository, order_item):
    mock_repository.get_by_id.return_value = order_item

    found = await order_item_service.get_order_item_by_id(order_item.id)

    mock_repository.get_by_id.assert_called_once_with(order_item.id)
    assert found.id == order_item.id


@pytest.mark.unit()
async def test_get_order_item_by_id_not_found(order_item_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(OrderItemNotFoundException):
        await order_item_service.get_order_item_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_order_items_by_order_id(
    order_item_service, mock_repository, order_item
):
    mock_repository.get_by_order_id.return_value = [order_item]

    items = await order_item_service.get_order_items_by_order_id(order_item.order_id)

    mock_repository.get_by_order_id.assert_called_once_with(order_item.order_id)
    assert len(items) == 1
    assert items[0].order_id == order_item.order_id


@pytest.mark.unit()
async def test_update_order_item(
    order_item_service, mock_repository, order_item, update_schema
):
    updated = OrderItem(
        order_id=update_schema.order_id,
        product_id=update_schema.product_id,
        quantity=update_schema.quantity,
        price=update_schema.price,
        id=order_item.id,
    )
    mock_repository.get_by_id.return_value = order_item
    mock_repository.update_by_id.return_value = updated

    result = await order_item_service.update_order_item(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.price == update_schema.price


@pytest.mark.unit()
async def test_update_order_item_not_found(
    order_item_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(OrderItemNotFoundException):
        await order_item_service.update_order_item(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_order_item_by_id(order_item_service, mock_repository, order_item):
    mock_repository.get_by_id.return_value = order_item
    mock_repository.delete_by_id.return_value = True

    is_deleted = await order_item_service.delete_order_item_by_id(order_item.id)

    mock_repository.get_by_id.assert_called_once_with(order_item.id)
    mock_repository.delete_by_id.assert_called_once_with(order_item.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_order_item_by_id_not_found(order_item_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(OrderItemNotFoundException):
        await order_item_service.delete_order_item_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
