import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.modules.coupons.schemas import CreateCouponSchema, UpdateCouponSchema


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateCouponSchema(
        discount_percentage=10.0,
        discount_amount=5.0,
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        usage_limit=100,
    )
    assert schema.discount_percentage == 10.0
    assert schema.usage_limit == 100


@pytest.mark.unit()
def test_create_schema_percentage_above_100_invalid():
    with pytest.raises(ValidationError):
        CreateCouponSchema(
            discount_percentage=150.0,
            discount_amount=5.0,
            expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
            usage_limit=100,
        )


@pytest.mark.unit()
def test_create_schema_negative_amount_invalid():
    with pytest.raises(ValidationError):
        CreateCouponSchema(
            discount_percentage=10.0,
            discount_amount=-1.0,
            expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
            usage_limit=100,
        )


@pytest.mark.unit()
def test_create_schema_usage_limit_zero_invalid():
    with pytest.raises(ValidationError):
        CreateCouponSchema(
            discount_percentage=10.0,
            discount_amount=5.0,
            expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
            usage_limit=0,
        )


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateCouponSchema(
        id=uuid.uuid4(),
        discount_percentage=20.0,
        discount_amount=10.0,
        expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
        usage_limit=50,
    )
    assert schema.discount_percentage == 20.0


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateCouponSchema(
            discount_percentage=20.0,
            discount_amount=10.0,
            expires_at=datetime(2030, 1, 1, tzinfo=timezone.utc),
            usage_limit=50,
        )
