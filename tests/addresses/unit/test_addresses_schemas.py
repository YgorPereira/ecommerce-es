import uuid

import pytest
from pydantic import ValidationError

from src.modules.addresses.schemas import (
    CreateAddressSchema,
    UpdateAddressSchema,
)


def _valid_data():
    return {
        "user_id": uuid.uuid4(),
        "address_line": "Rua das Flores",
        "city": "Recife",
        "state": "PE",
        "number": 100,
        "district": "Boa Viagem",
        "complement": "Apto 302",
    }


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateAddressSchema(**_valid_data())
    assert schema.city == "Recife"
    assert schema.number == 100


@pytest.mark.unit()
def test_create_schema_empty_complement_allowed():
    data = _valid_data()
    data["complement"] = ""
    schema = CreateAddressSchema(**data)
    assert schema.complement == ""


@pytest.mark.unit()
def test_create_schema_number_zero_invalid():
    data = _valid_data()
    data["number"] = 0
    with pytest.raises(ValidationError):
        CreateAddressSchema(**data)


@pytest.mark.unit()
def test_create_schema_empty_city_invalid():
    data = _valid_data()
    data["city"] = ""
    with pytest.raises(ValidationError):
        CreateAddressSchema(**data)


@pytest.mark.unit()
def test_create_schema_missing_user_id():
    data = _valid_data()
    del data["user_id"]
    with pytest.raises(ValidationError):
        CreateAddressSchema(**data)


@pytest.mark.unit()
def test_update_schema_valid():
    data = _valid_data()
    data["id"] = uuid.uuid4()
    schema = UpdateAddressSchema(**data)
    assert schema.district == "Boa Viagem"


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateAddressSchema(**_valid_data())
