import uuid

import pytest
from pydantic import ValidationError

from src.modules.payments.schemas import (
    CreatePaymentSchema,
    UpdatePaymentSchema,
)


def _valid_data():
    return {
        "order_id": uuid.uuid4(),
        "amount": 250.0,
        "method": "credit_card",
    }


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreatePaymentSchema(**_valid_data())
    assert schema.amount == 250.0
    assert schema.method == "credit_card"


@pytest.mark.unit()
def test_create_schema_negative_amount_invalid():
    data = _valid_data()
    data["amount"] = -1.0
    with pytest.raises(ValidationError):
        CreatePaymentSchema(**data)


@pytest.mark.unit()
def test_create_schema_empty_method_invalid():
    data = _valid_data()
    data["method"] = ""
    with pytest.raises(ValidationError):
        CreatePaymentSchema(**data)


@pytest.mark.unit()
def test_create_schema_missing_order_id():
    data = _valid_data()
    del data["order_id"]
    with pytest.raises(ValidationError):
        CreatePaymentSchema(**data)


@pytest.mark.unit()
def test_update_schema_valid():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    data["status"] = "paid"
    data["gateway_reference"] = "ref-123"
    schema = UpdatePaymentSchema(**data)
    assert schema.status == "paid"
    assert schema.gateway_reference == "ref-123"


@pytest.mark.unit()
def test_update_schema_gateway_reference_optional():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    data["status"] = "paid"
    schema = UpdatePaymentSchema(**data)
    assert schema.gateway_reference is None


@pytest.mark.unit()
def test_update_schema_missing_id():
    data = _valid_data()
    data["status"] = "paid"
    with pytest.raises(ValidationError):
        UpdatePaymentSchema(**data)
