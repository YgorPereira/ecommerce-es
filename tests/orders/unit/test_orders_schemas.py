import uuid

import pytest
from pydantic import ValidationError

from src.modules.orders.schemas import CreateOrderSchema, UpdateOrderSchema


def _valid_data():
    return {
        "user_id": uuid.uuid4(),
        "address_id": uuid.uuid4(),
        "coupon_id": uuid.uuid4(),
        "total_amount": 250.0,
    }


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateOrderSchema(**_valid_data())
    assert schema.total_amount == 250.0


@pytest.mark.unit()
def test_create_schema_without_coupon():
    data = _valid_data()
    del data["coupon_id"]
    schema = CreateOrderSchema(**data)
    assert schema.coupon_id is None


@pytest.mark.unit()
def test_create_schema_negative_total_invalid():
    data = _valid_data()
    data["total_amount"] = -1.0
    with pytest.raises(ValidationError):
        CreateOrderSchema(**data)


@pytest.mark.unit()
def test_create_schema_missing_address_id():
    data = _valid_data()
    del data["address_id"]
    with pytest.raises(ValidationError):
        CreateOrderSchema(**data)


@pytest.mark.unit()
def test_update_schema_valid():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    data["status"] = "paid"
    schema = UpdateOrderSchema(**data)
    assert schema.status == "paid"


@pytest.mark.unit()
def test_update_schema_missing_id():
    data = _valid_data()
    data["status"] = "paid"
    with pytest.raises(ValidationError):
        UpdateOrderSchema(**data)


@pytest.mark.unit()
def test_update_schema_empty_status_invalid():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    data["status"] = ""
    with pytest.raises(ValidationError):
        UpdateOrderSchema(**data)
