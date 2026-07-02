import uuid

import pytest
from pydantic import ValidationError

from src.modules.carts.schemas import CreateCartSchema, UpdateCartSchema


@pytest.mark.unit()
def test_create_schema_valid_with_coupon():
    schema = CreateCartSchema(
        user_id=uuid.uuid4(),
        coupon_id=uuid.uuid4(),
    )
    assert schema.coupon_id is not None


@pytest.mark.unit()
def test_create_schema_valid_without_coupon():
    schema = CreateCartSchema(user_id=uuid.uuid4())
    assert schema.coupon_id is None


@pytest.mark.unit()
def test_create_schema_missing_user_id():
    with pytest.raises(ValidationError):
        CreateCartSchema(coupon_id=uuid.uuid4())


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateCartSchema(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
    )
    assert schema.id is not None


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateCartSchema(user_id=uuid.uuid4())
