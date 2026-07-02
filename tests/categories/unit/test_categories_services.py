import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.categories.entity import Category
from src.modules.categories.exceptions import (
    CategoryNameAlreadyExistsException,
    CategoryNotFoundException,
)
from src.modules.categories.schemas import (
    CreateCategorySchema,
    UpdateCategorySchema,
)
from src.modules.categories.services import CategoryService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def category_service(mock_repository):
    return CategoryService(repository=mock_repository)


@pytest.fixture
def category():
    return Category(
        name="Eletrônicos",
        description="Aparelhos e dispositivos eletrônicos",
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(category):
    return CreateCategorySchema(
        name=category.name,
        description=category.description,
    )


@pytest.fixture
def update_schema(category):
    return UpdateCategorySchema(
        id=category.id,
        name="Eletrônicos e Informática",
        description="Descrição atualizada",
    )


@pytest.mark.unit()
async def test_create_category(
    category_service, mock_repository, create_schema, category
):
    mock_repository.get_by_name.return_value = None
    mock_repository.create.return_value = category

    created = await category_service.create_category(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created, Category)
    assert created.name == category.name
    assert created.description == category.description


@pytest.mark.unit()
async def test_create_category_name_already_exists(
    category_service, mock_repository, create_schema, category
):
    mock_repository.get_by_name.return_value = category

    with pytest.raises(CategoryNameAlreadyExistsException):
        await category_service.create_category(create_schema)

    mock_repository.get_by_name.assert_called_once_with(create_schema.name)
    mock_repository.create.assert_not_called()


@pytest.mark.unit()
async def test_get_all_categories(category_service, mock_repository, category):
    second = Category(
        name="Livros",
        description="Livros físicos e digitais",
        id=uuid.uuid4(),
    )
    mock_repository.get_all.return_value = [category, second]

    categories = await category_service.get_all_categories()

    mock_repository.get_all.assert_called_once()
    assert isinstance(categories, list)
    assert len(categories) == 2
    assert all(isinstance(c, Category) for c in categories)


@pytest.mark.unit()
async def test_get_all_categories_empty(category_service, mock_repository):
    mock_repository.get_all.return_value = []

    categories = await category_service.get_all_categories()

    mock_repository.get_all.assert_called_once()
    assert categories == []


@pytest.mark.unit()
async def test_get_category_by_id(category_service, mock_repository, category):
    mock_repository.get_by_id.return_value = category

    found = await category_service.get_category_by_id(category.id)

    mock_repository.get_by_id.assert_called_once_with(category.id)
    assert isinstance(found, Category)
    assert found.id == category.id


@pytest.mark.unit()
async def test_get_category_by_id_not_found(category_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(CategoryNotFoundException):
        await category_service.get_category_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_update_category(
    category_service, mock_repository, category, update_schema
):
    updated = Category(
        name=update_schema.name,
        description=update_schema.description,
        id=category.id,
    )
    mock_repository.get_by_id.return_value = category
    mock_repository.get_by_name.return_value = None
    mock_repository.update_by_id.return_value = updated

    result = await category_service.update_category(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert isinstance(result, Category)
    assert result.name == update_schema.name


@pytest.mark.unit()
async def test_update_category_not_found(
    category_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundException):
        await category_service.update_category(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_update_category_name_already_exists(
    category_service, mock_repository, category, update_schema
):
    other = Category(
        name=update_schema.name,
        description="Outra categoria",
        id=uuid.uuid4(),
    )
    mock_repository.get_by_id.return_value = category
    mock_repository.get_by_name.return_value = other

    with pytest.raises(CategoryNameAlreadyExistsException):
        await category_service.update_category(update_schema)

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_category_by_id(category_service, mock_repository, category):
    mock_repository.get_by_id.return_value = category
    mock_repository.delete_by_id.return_value = True

    is_deleted = await category_service.delete_category_by_id(category.id)

    mock_repository.get_by_id.assert_called_once_with(category.id)
    mock_repository.delete_by_id.assert_called_once_with(category.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_category_by_id_not_found(category_service, mock_repository):
    non_existent_id = uuid.uuid4()
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CategoryNotFoundException):
        await category_service.delete_category_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
