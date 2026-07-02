import uuid

import pytest
from pydantic import ValidationError

from src.modules.order_items.schemas import (
    CreateOrderItemSchema,
    UpdateOrderItemSchema,
)


def _valid_data():
    return {
        "order_id": uuid.uuid4(),
        "product_id": uuid.uuid4(),
        "quantity": 2,
        "price": 99.9,
    }


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateOrderItemSchema(**_valid_data())
    assert schema.quantity == 2
    assert schema.price == 99.9


@pytest.mark.unit()
def test_create_schema_quantity_zero_invalid():
    data = _valid_data()
    data["quantity"] = 0
    with pytest.raises(ValidationError):
        CreateOrderItemSchema(**data)


@pytest.mark.unit()
def test_create_schema_negative_price_invalid():
    data = _valid_data()
    data["price"] = -1.0
    with pytest.raises(ValidationError):
        CreateOrderItemSchema(**data)


@pytest.mark.unit()
def test_create_schema_missing_order_id():
    data = _valid_data()
    del data["order_id"]
    with pytest.raises(ValidationError):
        CreateOrderItemSchema(**data)


@pytest.mark.unit()
def test_update_schema_valid():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    schema = UpdateOrderItemSchema(**data)
    assert schema.id is not None


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateOrderItemSchema(**_valid_data())
