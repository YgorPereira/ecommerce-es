import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from src.modules.cart_items.entity import CartItem
from src.modules.carts.checkout import CheckoutService
from src.modules.carts.entity import Cart
from src.modules.carts.exceptions import CartNotFoundException, EmptyCartException
from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import CouponExpiredException
from src.modules.inventories.exceptions import InsufficientStockException
from src.modules.orders.entity import Order
from src.modules.products.entity import Product
from src.modules.products.exceptions import ProductNotFoundException


@pytest.fixture
def repos():
    return {
        "cart": AsyncMock(),
        "cart_item": AsyncMock(),
        "product": AsyncMock(),
        "inventory": AsyncMock(),
        "coupon": AsyncMock(),
        "order": AsyncMock(),
        "order_item": AsyncMock(),
    }


@pytest.fixture
def service(repos):
    return CheckoutService(
        repos["cart"],
        repos["cart_item"],
        repos["product"],
        repos["inventory"],
        repos["coupon"],
        repos["order"],
        repos["order_item"],
    )


@pytest.fixture
def product():
    return Product(
        name="Notebook",
        price=100.0,
        description="x",
        category_id=uuid.uuid4(),
        id=uuid.uuid4(),
    )


@pytest.fixture
def cart():
    return Cart(
        user_id=uuid.uuid4(),
        coupon_id=None,
        created_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


def _configure_happy_path(repos, cart, product, quantity=2):
    repos["cart"].get_by_id.return_value = cart
    repos["cart_item"].get_by_cart_id.return_value = [
        CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            id=uuid.uuid4(),
        )
    ]
    repos["product"].get_by_id.return_value = product
    repos["inventory"].decrement.return_value = True
    repos["order"].create.return_value = Order(
        user_id=cart.user_id,
        address_id=uuid.uuid4(),
        total_amount=0.0,
        status="pending",
        created_at=datetime.now(timezone.utc),
        id=uuid.uuid4(),
    )


@pytest.mark.unit()
async def test_checkout_success_creates_order_and_items(repos, service, cart, product):
    _configure_happy_path(repos, cart, product, quantity=2)
    address_id = uuid.uuid4()

    await service.checkout(cart.id, address_id)

    # reservou o estoque
    repos["inventory"].decrement.assert_awaited_once_with(product.id, 2)
    # criou o pedido com total = 2 * 100
    order_arg = repos["order"].create.call_args.args[0]
    assert order_arg.total_amount == 200.0
    assert order_arg.user_id == cart.user_id
    assert order_arg.address_id == address_id
    # criou um order_item
    repos["order_item"].create.assert_awaited_once()


@pytest.mark.unit()
async def test_checkout_applies_valid_coupon(repos, service, cart, product):
    _configure_happy_path(repos, cart, product, quantity=2)
    cart.coupon_id = uuid.uuid4()
    repos["coupon"].get_by_id.return_value = Coupon(
        discount_percentage=10.0,
        discount_amount=0.0,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        usage_limit=5,
        id=cart.coupon_id,
    )

    await service.checkout(cart.id, uuid.uuid4())

    order_arg = repos["order"].create.call_args.args[0]
    # 200 - 10% = 180
    assert order_arg.total_amount == 180.0


@pytest.mark.unit()
async def test_checkout_cart_not_found(repos, service):
    repos["cart"].get_by_id.return_value = None

    with pytest.raises(CartNotFoundException):
        await service.checkout(uuid.uuid4(), uuid.uuid4())


@pytest.mark.unit()
async def test_checkout_empty_cart(repos, service, cart):
    repos["cart"].get_by_id.return_value = cart
    repos["cart_item"].get_by_cart_id.return_value = []

    with pytest.raises(EmptyCartException):
        await service.checkout(cart.id, uuid.uuid4())

    repos["order"].create.assert_not_called()


@pytest.mark.unit()
async def test_checkout_insufficient_stock_creates_no_order(
    repos, service, cart, product
):
    _configure_happy_path(repos, cart, product)
    repos["inventory"].decrement.return_value = False

    with pytest.raises(InsufficientStockException):
        await service.checkout(cart.id, uuid.uuid4())

    repos["order"].create.assert_not_called()


@pytest.mark.unit()
async def test_checkout_product_not_found(repos, service, cart, product):
    _configure_happy_path(repos, cart, product)
    repos["product"].get_by_id.return_value = None

    with pytest.raises(ProductNotFoundException):
        await service.checkout(cart.id, uuid.uuid4())

    repos["order"].create.assert_not_called()


@pytest.mark.unit()
async def test_checkout_expired_coupon(repos, service, cart, product):
    _configure_happy_path(repos, cart, product)
    cart.coupon_id = uuid.uuid4()
    repos["coupon"].get_by_id.return_value = Coupon(
        discount_percentage=10.0,
        discount_amount=0.0,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        usage_limit=5,
        id=cart.coupon_id,
    )

    with pytest.raises(CouponExpiredException):
        await service.checkout(cart.id, uuid.uuid4())

    repos["order"].create.assert_not_called()
