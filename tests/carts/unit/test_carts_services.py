import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.carts.entity import Cart
from src.modules.carts.exceptions import CartNotFoundException
from src.modules.carts.schemas import CreateCartSchema, UpdateCartSchema
from src.modules.carts.services import CartService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def cart_service(mock_repository):
    return CartService(repository=mock_repository)


@pytest.fixture
def cart():
    return Cart(
        user_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(cart):
    return CreateCartSchema(
        user_id=cart.user_id,
        coupon_id=cart.coupon_id,
    )


@pytest.fixture
def update_schema(cart):
    return UpdateCartSchema(
        id=cart.id,
        user_id=cart.user_id,
        coupon_id=None,
    )


@pytest.mark.unit()
async def test_create_cart(cart_service, mock_repository, create_schema, cart):
    mock_repository.create.return_value = cart

    created = await cart_service.create_cart(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Cart)
    assert created.user_id == cart.user_id


@pytest.mark.unit()
async def test_create_cart_sets_created_at(
    cart_service, mock_repository, create_schema
):
    async def echo(entity):
        return entity

    mock_repository.create.side_effect = echo

    created = await cart_service.create_cart(create_schema)

    assert created.created_at is not None


@pytest.mark.unit()
async def test_get_all_carts(cart_service, mock_repository, cart):
    mock_repository.get_all.return_value = [cart, cart]

    carts = await cart_service.get_all_carts()

    mock_repository.get_all.assert_called_once()
    assert len(carts) == 2


@pytest.mark.unit()
async def test_get_cart_by_id(cart_service, mock_repository, cart):
    mock_repository.get_by_id.return_value = cart

    found = await cart_service.get_cart_by_id(cart.id)

    mock_repository.get_by_id.assert_called_once_with(cart.id)
    assert found.id == cart.id


@pytest.mark.unit()
async def test_get_cart_by_id_not_found(cart_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(CartNotFoundException):
        await cart_service.get_cart_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_carts_by_user_id(cart_service, mock_repository, cart):
    mock_repository.get_by_user_id.return_value = [cart]

    carts = await cart_service.get_carts_by_user_id(cart.user_id)

    mock_repository.get_by_user_id.assert_called_once_with(cart.user_id)
    assert len(carts) == 1
    assert carts[0].user_id == cart.user_id


@pytest.mark.unit()
async def test_update_cart_preserves_created_at(
    cart_service, mock_repository, cart, update_schema
):
    mock_repository.get_by_id.return_value = cart

    async def echo(entity):
        return entity

    mock_repository.update_by_id.side_effect = echo

    result = await cart_service.update_cart(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert result.created_at == cart.created_at
    assert result.coupon_id is None


@pytest.mark.unit()
async def test_update_cart_not_found(cart_service, mock_repository, update_schema):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CartNotFoundException):
        await cart_service.update_cart(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_cart_by_id(cart_service, mock_repository, cart):
    mock_repository.get_by_id.return_value = cart
    mock_repository.delete_by_id.return_value = True

    is_deleted = await cart_service.delete_cart_by_id(cart.id)

    mock_repository.get_by_id.assert_called_once_with(cart.id)
    mock_repository.delete_by_id.assert_called_once_with(cart.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_cart_by_id_not_found(cart_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CartNotFoundException):
        await cart_service.delete_cart_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
