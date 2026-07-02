import uuid

import pytest
from pydantic import ValidationError

from src.modules.products.schemas import CreateProductSchema, UpdateProductSchema


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateProductSchema(
        name="Notebook Gamer",
        price=4999.90,
        description="Notebook com placa de vídeo dedicada",
        category_id=uuid.uuid4(),
    )
    assert schema.name == "Notebook Gamer"
    assert schema.price == 4999.90


@pytest.mark.unit()
def test_create_schema_name_too_short():
    with pytest.raises(ValidationError):
        CreateProductSchema(
            name="AB",
            price=100.0,
            description="Descrição válida",
            category_id=uuid.uuid4(),
        )


@pytest.mark.unit()
def test_create_schema_price_zero_invalid():
    with pytest.raises(ValidationError):
        CreateProductSchema(
            name="Produto Teste",
            price=0,
            description="Descrição válida",
            category_id=uuid.uuid4(),
        )


@pytest.mark.unit()
def test_create_schema_price_negative_invalid():
    with pytest.raises(ValidationError):
        CreateProductSchema(
            name="Produto Teste",
            price=-10,
            description="Descrição válida",
            category_id=uuid.uuid4(),
        )


@pytest.mark.unit()
def test_create_schema_description_empty():
    with pytest.raises(ValidationError):
        CreateProductSchema(
            name="Produto Teste",
            price=100.0,
            description="",
            category_id=uuid.uuid4(),
        )


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateProductSchema(
        id=uuid.uuid4(),
        name="Produto Atualizado",
        price=150.0,
        description="Descrição atualizada",
        category_id=uuid.uuid4(),
    )
    assert schema.name == "Produto Atualizado"


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateProductSchema(
            name="Produto Atualizado",
            price=150.0,
            description="Descrição atualizada",
            category_id=uuid.uuid4(),
        )
