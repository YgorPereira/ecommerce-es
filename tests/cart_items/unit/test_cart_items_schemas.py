import uuid

import pytest
from pydantic import ValidationError

from src.modules.cart_items.schemas import (
    CreateCartItemSchema,
    UpdateCartItemSchema,
)


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateCartItemSchema(
        cart_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=2,
    )
    assert schema.quantity == 2


@pytest.mark.unit()
def test_create_schema_quantity_zero_invalid():
    with pytest.raises(ValidationError):
        CreateCartItemSchema(
            cart_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            quantity=0,
        )


@pytest.mark.unit()
def test_create_schema_negative_quantity_invalid():
    with pytest.raises(ValidationError):
        CreateCartItemSchema(
            cart_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            quantity=-1,
        )


@pytest.mark.unit()
def test_create_schema_missing_cart_id():
    with pytest.raises(ValidationError):
        CreateCartItemSchema(
            product_id=uuid.uuid4(),
            quantity=1,
        )


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateCartItemSchema(
        id=uuid.uuid4(),
        cart_id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=3,
    )
    assert schema.quantity == 3


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateCartItemSchema(
            cart_id=uuid.uuid4(),
            product_id=uuid.uuid4(),
            quantity=3,
        )
