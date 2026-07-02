from datetime import datetime, timedelta, timezone

import pytest

from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import (
    CouponExpiredException,
    CouponUsageLimitReachedException,
)
from src.modules.coupons.validation import assert_coupon_applicable


def _coupon(usage_limit=10, expires_in_days=1):
    return Coupon(
        discount_percentage=10.0,
        discount_amount=0.0,
        expires_at=datetime.now(timezone.utc) + timedelta(days=expires_in_days),
        usage_limit=usage_limit,
    )


@pytest.mark.unit()
def test_valid_coupon_passes():
    now = datetime.now(timezone.utc)
    assert_coupon_applicable(_coupon(), now)  # não levanta


@pytest.mark.unit()
def test_is_valid_true():
    now = datetime.now(timezone.utc)
    assert _coupon().is_valid(now) is True


@pytest.mark.unit()
def test_expired_coupon_raises():
    now = datetime.now(timezone.utc)
    with pytest.raises(CouponExpiredException):
        assert_coupon_applicable(_coupon(expires_in_days=-1), now)


@pytest.mark.unit()
def test_no_usage_left_raises():
    now = datetime.now(timezone.utc)
    with pytest.raises(CouponUsageLimitReachedException):
        assert_coupon_applicable(_coupon(usage_limit=0), now)


@pytest.mark.unit()
def test_is_valid_false_when_expired():
    now = datetime.now(timezone.utc)
    assert _coupon(expires_in_days=-1).is_valid(now) is False


@pytest.mark.unit()
def test_is_valid_false_when_no_usage():
    now = datetime.now(timezone.utc)
    assert _coupon(usage_limit=0).is_valid(now) is False
