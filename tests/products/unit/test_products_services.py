import uuid
from unittest.mock import AsyncMock

import pytest

from src.modules.products.entity import Product
from src.modules.products.exceptions import (
    ProductNameAlreadyExistsException,
    ProductNotFoundException,
)
from src.modules.products.schemas import CreateProductSchema, UpdateProductSchema
from src.modules.products.services import ProductService


@pytest.fixture
def mock_repository():
    return AsyncMock()


@pytest.fixture
def product_service(mock_repository):
    return ProductService(repository=mock_repository)


@pytest.fixture
def product():
    return Product(
        name="Notebook Gamer",
        price=4999.90,
        description="Notebook com placa de vídeo dedicada",
        category_id=uuid.uuid4(),
        id=uuid.uuid4(),
    )


@pytest.fixture
def create_schema(product):
    return CreateProductSchema(
        name=product.name,
        price=product.price,
        description=product.description,
        category_id=product.category_id,
    )


@pytest.fixture
def update_schema(product):
    return UpdateProductSchema(
        id=product.id,
        name="Notebook Gamer Atualizado",
        price=5299.90,
        description="Descrição atualizada",
        category_id=product.category_id,
    )


@pytest.mark.unit()
async def test_create_product(product_service, mock_repository, create_schema, product):
    mock_repository.get_by_name.return_value = None
    mock_repository.create.return_value = product

    created_product = await product_service.create_product(create_schema)

    mock_repository.create.assert_called_once()
    assert isinstance(created_product, Product)
    assert created_product.name == product.name
    assert created_product.price == product.price


@pytest.mark.unit()
async def test_create_product_name_already_exists(
    product_service, mock_repository, create_schema, product
):
    mock_repository.get_by_name.return_value = product

    with pytest.raises(ProductNameAlreadyExistsException):
        await product_service.create_product(create_schema)

    mock_repository.get_by_name.assert_called_once_with(create_schema.name)
    mock_repository.create.assert_not_called()


@pytest.mark.unit()
async def test_get_all_products(product_service, mock_repository, product):
    second_product = Product(
        name="Mouse Gamer",
        price=199.90,
        description="Mouse com sensor óptico",
        category_id=uuid.uuid4(),
        id=uuid.uuid4(),
    )
    mock_repository.get_all.return_value = [product, second_product]

    products = await product_service.get_all_products()

    mock_repository.get_all.assert_called_once()
    assert isinstance(products, list)
    assert len(products) == 2
    assert all(isinstance(p, Product) for p in products)


@pytest.mark.unit()
async def test_get_all_products_empty(product_service, mock_repository):
    mock_repository.get_all.return_value = []

    products = await product_service.get_all_products()

    mock_repository.get_all.assert_called_once()
    assert products == []


@pytest.mark.unit()
async def test_get_product_by_id(product_service, mock_repository, product):
    mock_repository.get_by_id.return_value = product

    found_product = await product_service.get_product_by_id(product.id)

    mock_repository.get_by_id.assert_called_once_with(product.id)
    assert isinstance(found_product, Product)
    assert found_product.id == product.id
    assert found_product.name == product.name


@pytest.mark.unit()
async def test_get_product_by_id_not_found(product_service, mock_repository):
    mock_repository.get_by_id.return_value = None
    non_existent_id = uuid.uuid4()

    with pytest.raises(ProductNotFoundException):
        await product_service.get_product_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)


@pytest.mark.unit()
async def test_get_products_by_category_id(product_service, mock_repository, product):
    mock_repository.get_by_category_id.return_value = [product]

    products = await product_service.get_products_by_category_id(product.category_id)

    mock_repository.get_by_category_id.assert_called_once_with(product.category_id)
    assert len(products) == 1
    assert products[0].category_id == product.category_id


@pytest.mark.unit()
async def test_update_product(product_service, mock_repository, product, update_schema):
    updated = Product(
        name=update_schema.name,
        price=update_schema.price,
        description=update_schema.description,
        category_id=update_schema.category_id,
        id=product.id,
    )
    mock_repository.get_by_id.return_value = product
    mock_repository.get_by_name.return_value = None
    mock_repository.update_by_id.return_value = updated

    result = await product_service.update_product(update_schema)

    mock_repository.update_by_id.assert_called_once()
    assert isinstance(result, Product)
    assert result.name == update_schema.name
    assert result.price == update_schema.price


@pytest.mark.unit()
async def test_update_product_name_already_exists(
    product_service, mock_repository, product, update_schema
):
    other_product = Product(
        name=update_schema.name,
        price=100.0,
        description="Outro produto",
        category_id=uuid.uuid4(),
        id=uuid.uuid4(),
    )
    mock_repository.get_by_id.return_value = product
    mock_repository.get_by_name.return_value = other_product

    with pytest.raises(ProductNameAlreadyExistsException):
        await product_service.update_product(update_schema)

    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_update_product_not_found(
    product_service, mock_repository, update_schema
):
    mock_repository.get_by_id.return_value = None

    with pytest.raises(ProductNotFoundException):
        await product_service.update_product(update_schema)

    mock_repository.get_by_id.assert_called_once()
    mock_repository.update_by_id.assert_not_called()


@pytest.mark.unit()
async def test_delete_product_by_id(product_service, mock_repository, product):
    mock_repository.get_by_id.return_value = product
    mock_repository.delete_by_id.return_value = True

    is_deleted = await product_service.delete_product_by_id(product.id)

    mock_repository.get_by_id.assert_called_once_with(product.id)
    mock_repository.delete_by_id.assert_called_once_with(product.id)
    assert is_deleted is True


@pytest.mark.unit()
async def test_delete_product_by_id_not_found(product_service, mock_repository):
    non_existent_id = uuid.uuid4()

    mock_repository.get_by_id.return_value = None

    with pytest.raises(ProductNotFoundException):
        await product_service.delete_product_by_id(non_existent_id)

    mock_repository.get_by_id.assert_called_once_with(non_existent_id)
