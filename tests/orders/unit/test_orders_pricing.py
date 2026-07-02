from datetime import datetime, timedelta, timezone

import pytest

from src.modules.coupons.entity import Coupon
from src.modules.orders.pricing import LineItem, calculate_subtotal, calculate_total


def _coupon(percentage=0.0, amount=0.0):
    return Coupon(
        discount_percentage=percentage,
        discount_amount=amount,
        expires_at=datetime.now(timezone.utc) + timedelta(days=1),
        usage_limit=10,
    )


@pytest.mark.unit()
def test_subtotal():
    items = [LineItem(price=100.0, quantity=2), LineItem(price=50.0, quantity=1)]
    assert calculate_subtotal(items) == 250.0


@pytest.mark.unit()
def test_total_without_coupon():
    items = [LineItem(price=100.0, quantity=2), LineItem(price=50.0, quantity=1)]
    assert calculate_total(items) == 250.0


@pytest.mark.unit()
def test_total_empty_items():
    assert calculate_total([]) == 0.0


@pytest.mark.unit()
def test_total_with_percentage_coupon():
    items = [LineItem(price=100.0, quantity=2)]
    assert calculate_total(items, _coupon(percentage=10.0)) == 180.0


@pytest.mark.unit()
def test_total_with_amount_coupon():
    items = [LineItem(price=100.0, quantity=2)]
    assert calculate_total(items, _coupon(amount=30.0)) == 170.0


@pytest.mark.unit()
def test_total_with_percentage_and_amount():
    items = [LineItem(price=100.0, quantity=2)]
    # 200 - 10% = 180 ; 180 - 5 = 175
    assert calculate_total(items, _coupon(percentage=10.0, amount=5.0)) == 175.0


@pytest.mark.unit()
def test_total_never_negative():
    items = [LineItem(price=10.0, quantity=1)]
    assert calculate_total(items, _coupon(amount=999.0)) == 0.0


@pytest.mark.unit()
def test_total_is_rounded():
    items = [LineItem(price=10.0, quantity=3)]
    # 30 - 33% = 20.10
    assert calculate_total(items, _coupon(percentage=33.0)) == 20.1
