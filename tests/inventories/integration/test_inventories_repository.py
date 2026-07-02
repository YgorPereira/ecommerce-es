import uuid

import pytest

from src.modules.categories.entity import Category
from src.modules.inventories.entity import Inventory
from src.modules.products.entity import Product


@pytest.fixture(scope="function")
async def persisted_product(category_repository, product_repository):
    unique = str(uuid.uuid4())
    category = await category_repository.create(
        Category(name=f"Categoria {unique}", description="teste")
    )
    return await product_repository.create(
        Product(
            name=f"Produto {unique}",
            price=100.0,
            description="teste",
            category_id=category.id,
        )
    )


@pytest.fixture(scope="function")
async def last_unit_inventory(inventory_repository, persisted_product):
    """Estoque com apenas UMA unidade disponível."""
    return await inventory_repository.create(
        Inventory(product_id=persisted_product.id, quantity=1)
    )


@pytest.mark.integration()
async def test_decrement_reduces_quantity(
    inventory_repository, last_unit_inventory, persisted_product
):
    ok = await inventory_repository.decrement(persisted_product.id, 1)

    assert ok is True
    updated = await inventory_repository.get_by_product_id(persisted_product.id)
    assert updated.quantity == 0


@pytest.mark.integration()
async def test_cannot_oversell_last_unit(
    inventory_repository, last_unit_inventory, persisted_product
):
    """Duas baixas da última unidade: a primeira passa, a segunda falha."""
    first = await inventory_repository.decrement(persisted_product.id, 1)
    second = await inventory_repository.decrement(persisted_product.id, 1)

    assert first is True
    assert second is False

    final = await inventory_repository.get_by_product_id(persisted_product.id)
    assert final.quantity == 0


@pytest.mark.integration()
async def test_decrement_more_than_available_fails(
    inventory_repository, last_unit_inventory, persisted_product
):
    ok = await inventory_repository.decrement(persisted_product.id, 2)

    assert ok is False
    unchanged = await inventory_repository.get_by_product_id(persisted_product.id)
    assert unchanged.quantity == 1


@pytest.mark.integration()
async def test_decrement_unknown_product_returns_false(inventory_repository):
    ok = await inventory_repository.decrement(uuid.uuid4(), 1)
    assert ok is False
