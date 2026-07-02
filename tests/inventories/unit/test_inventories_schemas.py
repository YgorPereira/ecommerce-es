import uuid

import pytest
from pydantic import ValidationError

from src.modules.inventories.schemas import (
    CreateInventorySchema,
    UpdateInventorySchema,
)


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateInventorySchema(
        product_id=uuid.uuid4(),
        quantity=50,
    )
    assert schema.quantity == 50


@pytest.mark.unit()
def test_create_schema_quantity_zero_valid():
    schema = CreateInventorySchema(
        product_id=uuid.uuid4(),
        quantity=0,
    )
    assert schema.quantity == 0


@pytest.mark.unit()
def test_create_schema_negative_quantity_invalid():
    with pytest.raises(ValidationError):
        CreateInventorySchema(
            product_id=uuid.uuid4(),
            quantity=-1,
        )


@pytest.mark.unit()
def test_create_schema_missing_product_id():
    with pytest.raises(ValidationError):
        CreateInventorySchema(quantity=10)


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateInventorySchema(
        id=uuid.uuid4(),
        product_id=uuid.uuid4(),
        quantity=30,
    )
    assert schema.quantity == 30


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateInventorySchema(
            product_id=uuid.uuid4(),
            quantity=30,
        )
