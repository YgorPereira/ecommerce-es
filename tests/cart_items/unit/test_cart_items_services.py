import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.cart_items.entity import CartItem
from src.modules.cart_items.exceptions import CartItemNotFoundException
from src.modules.cart_items.schemas import (
    CreateCartItemSchema,
    UpdateCartItemSchema,
)
from src.modules.cart_items.services import CartItemService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def cart_item_service(mock_repository):
    return CartItemService(repository=mock_repository)


@pytest.fixture
def cart_item():
    return CartItem(
        cart_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=2,
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(cart_item):
    return CreateCartItemSchema(
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
    )


@pytest.fixture
def update_schema(cart_item):
    return UpdateCartItemSchema(
        id=cart_item.id,
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=5,
    )


@pytest.mark.unit()
async def test_create_cart_item(
    cart_item_service, mock_repository, create_schema, cart_item
):
    mock_repository.create.return_value = cart_item

    created = await cart_item_service.create_cart_item(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, CartItem)
    assert created.quantity == cart_item.quantity


@pytest.mark.unit()
async def test_get_all_cart_items(cart_item_service, mock_repository, cart_item):
    mock_repository.get_all.return_value = [cart_item, cart_item]

    items = await cart_item_service.get_all_cart_items()

    mock_repository.get_all.assert_called_once()
    assert len(items) == 2


@pytest.mark.unit()
async def test_get_all_cart_items_empty(cart_item_service, mock_repository):
    mock_repository.get_all.return_value = []

    items = await cart_item_service.get_all_cart_items()

    mock_repository.get_all.assert_called_once()
    assert items == []


@pytest.mark.unit()
async def test_get_cart_item_by_id(cart_item_service, mock_repository, cart_item):
    mock_repository.get_by_id.return_value = cart_item

    found = await cart_item_service.get_cart_item_by_id(cart_item.id)

    mock_repository.get_by_id.assert_called_once_with(cart_item.id)
    assert found.id == cart_item.id


@pytest.mark.unit()
async def test_get_cart_item_by_id_not_found(cart_item_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(CartItemNotFoundException):
        await cart_item_service.get_cart_item_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_cart_items_by_cart_id(cart_item_service, mock_repository, cart_item):
    mock_repository.get_by_cart_id.return_value = [cart_item]

    items = await cart_item_service.get_cart_items_by_cart_id(cart_item.cart_id)

    mock_repository.get_by_cart_id.assert_called_once_with(cart_item.cart_id)
    assert len(items) == 1
    assert items[0].cart_id == cart_item.cart_id


@pytest.mark.unit()
async def test_update_cart_item(
    cart_item_service, mock_repository, cart_item, update_schema
):
    updated = CartItem(
        cart_id=update_schema.cart_id,
        product_id=update_schema.product_id,
        quantity=update_schema.quantity,
        id=cart_item.id,
    )
    mock_repository.get_by_id.return_value = cart_item
    mock_repository.update_by_id.return_value = updated

    result = await cart_item_service.update_cart_item(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.quantity == update_schema.quantity


@pytest.mark.unit()
async def test_update_cart_item_not_found(
    cart_item_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CartItemNotFoundException):
        await cart_item_service.update_cart_item(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_cart_item_by_id(cart_item_service, mock_repository, cart_item):
    mock_repository.get_by_id.return_value = cart_item
    mock_repository.delete_by_id.return_value = True

    is_deleted = await cart_item_service.delete_cart_item_by_id(cart_item.id)

    mock_repository.get_by_id.assert_called_once_with(cart_item.id)
    mock_repository.delete_by_id.assert_called_once_with(cart_item.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_cart_item_by_id_not_found(cart_item_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CartItemNotFoundException):
        await cart_item_service.delete_cart_item_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
