import uuid

import pytest

from src.modules.categories.entity import Category
from src.modules.products.entity import Product


@pytest.fixture(scope="function")
async def persisted_category(category_repository):
    unique = str(uuid.uuid4())
    return await category_repository.create(
        Category(name=f"Categoria {unique}", description="Categoria de teste")
    )


@pytest.fixture
def product(persisted_category):
    return Product(
        name="Notebook Gamer",
        price=4999.90,
        description="Notebook com placa de vídeo dedicada",
        category_id=persisted_category.id,
    )


@pytest.fixture(scope="function")
async def persisted_product(product_repository, product):
    return await product_repository.create(product)


@pytest.mark.integration()
async def test_create_product(product_repository, product):
    created = await product_repository.create(product)

    assert isinstance(created, Product)
    assert created.id is not None
    assert created.name == product.name
    assert created.price == product.price
    assert created.category_id == product.category_id


@pytest.mark.integration()
async def test_get_product_by_id(product_repository, persisted_product, product):
    found = await product_repository.get_by_id(persisted_product.id)

    assert isinstance(found, Product)
    assert found.id == persisted_product.id
    assert found.name == product.name
    assert found.category_id == product.category_id


@pytest.mark.integration()
async def test_get_product_by_name(product_repository, persisted_product):
    found = await product_repository.get_by_name(persisted_product.name)

    assert isinstance(found, Product)
    assert found.id == persisted_product.id
    assert found.name == persisted_product.name


@pytest.mark.integration()
async def test_get_products_by_category_id(
    product_repository, persisted_product, persisted_category
):
    products = await product_repository.get_by_category_id(persisted_category.id)

    assert isinstance(products, list)
    assert len(products) == 1
    assert products[0].id == persisted_product.id
    assert products[0].category_id == persisted_category.id


@pytest.mark.integration()
async def test_update_product_by_id(product_repository, persisted_product):
    persisted_product.name = "Notebook Atualizado"
    persisted_product.price = 5299.90

    updated = await product_repository.update_by_id(persisted_product)

    assert isinstance(updated, Product)
    assert updated.id == persisted_product.id
    assert updated.name == "Notebook Atualizado"
    assert updated.price == 5299.90


@pytest.mark.integration()
async def test_delete_product_by_id(product_repository, persisted_product):
    is_deleted = await product_repository.delete_by_id(persisted_product.id)

    assert is_deleted


@pytest.mark.integration()
async def test_get_all_products_empty(product_repository):
    products = await product_repository.get_all()
    assert products == []


@pytest.mark.integration()
async def test_get_all_products(product_repository, persisted_category):
    await product_repository.create(
        Product(
            name="Notebook Gamer",
            price=4999.90,
            description="Notebook",
            category_id=persisted_category.id,
        )
    )
    await product_repository.create(
        Product(
            name="Mouse Gamer",
            price=199.90,
            description="Mouse óptico",
            category_id=persisted_category.id,
        )
    )

    products = await product_repository.get_all()

    assert isinstance(products, list)
    assert all(isinstance(p, Product) for p in products)
    assert len(products) == 2


@pytest.mark.integration()
async def test_get_product_by_id_not_found(product_repository):
    found = await product_repository.get_by_id(uuid.uuid4())
    assert found is None


@pytest.mark.integration()
async def test_get_product_by_name_not_found(product_repository):
    found = await product_repository.get_by_name("Produto Inexistente")
    assert found is None


@pytest.mark.integration()
async def test_delete_product_by_id_not_found(product_repository):
    is_deleted = await product_repository.delete_by_id(uuid.uuid4())
    assert not is_deleted
