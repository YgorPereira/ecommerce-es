import uuid

import pytest
from pydantic import ValidationError

from src.modules.categories.schemas import (
    CreateCategorySchema,
    UpdateCategorySchema,
)


@pytest.mark.unit()
def test_create_schema_valid():
    schema = CreateCategorySchema(
        name="Eletrônicos",
        description="Aparelhos e dispositivos eletrônicos",
    )
    assert schema.name == "Eletrônicos"
    assert schema.description == "Aparelhos e dispositivos eletrônicos"


@pytest.mark.unit()
def test_create_schema_name_too_short():
    with pytest.raises(ValidationError):
        CreateCategorySchema(
            name="AB",
            description="Descrição válida",
        )


@pytest.mark.unit()
def test_create_schema_description_empty():
    with pytest.raises(ValidationError):
        CreateCategorySchema(
            name="Categoria Teste",
            description="",
        )


@pytest.mark.unit()
def test_update_schema_valid():
    schema = UpdateCategorySchema(
        id=uuid.uuid4(),
        name="Categoria Atualizada",
        description="Descrição atualizada",
    )
    assert schema.name == "Categoria Atualizada"


@pytest.mark.unit()
def test_update_schema_missing_id():
    with pytest.raises(ValidationError):
        UpdateCategorySchema(
            name="Categoria Atualizada",
            description="Descrição atualizada",
        )
