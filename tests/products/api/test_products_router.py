import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.modules.auth.dependencies import get_current_user
from src.modules.auth.permissions import require_admin
from src.modules.products.entity import Product
from src.modules.products.exceptions import (
    ProductNameAlreadyExistsException,
    ProductNotFoundException,
)
from src.modules.products.router import get_product_service
from src.modules.users.entity import User
from src.modules.users.enums.role import UserRole


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin():
    return User(
        id=uuid.uuid4(),
        name="Admin",
        cpf="12345678900",
        email="admin@gmail.com",
        password="senha1234",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def admin_client(client, admin):
    app.dependency_overrides[get_current_user] = lambda: admin
    app.dependency_overrides[require_admin] = lambda: admin
    yield client
    app.dependency_overrides.pop(get_current_user, None)
    app.dependency_overrides.pop(require_admin, None)


@pytest.fixture
def mock_product_service():
    service = AsyncMock()
    app.dependency_overrides[get_product_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


@pytest.fixture
def product():
    return Product(
        id=uuid.uuid4(),
        name="Notebook Gamer",
        price=4999.90,
        description="Notebook com placa de vídeo dedicada",
        category_id=uuid.uuid4(),
    )


@pytest.mark.api
def test_create_product(admin_client, mock_product_service, product):
    mock_product_service.create_product.return_value = product

    response = admin_client.post(
        "/products",
        json={
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category_id": str(product.category_id),
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["id"] == str(product.id)
    assert body["name"] == product.name
    assert body["price"] == product.price
    assert body["category_id"] == str(product.category_id)

    mock_product_service.create_product.assert_awaited_once()


@pytest.mark.api
def test_create_product_name_already_exists(admin_client, mock_product_service):
    mock_product_service.create_product.side_effect = (
        ProductNameAlreadyExistsException()
    )

    response = admin_client.post(
        "/products",
        json={
            "name": "Notebook Gamer",
            "price": 4999.90,
            "description": "Descrição válida",
            "category_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 409


@pytest.mark.api
def test_create_product_invalid_price(admin_client):
    response = admin_client.post(
        "/products",
        json={
            "name": "Notebook Gamer",
            "price": 0,
            "description": "Descrição válida",
            "category_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 422


@pytest.mark.api
def test_get_product_by_id(client, mock_product_service, product):
    mock_product_service.get_product_by_id.return_value = product

    response = client.get(f"/products/{product.id}")

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == str(product.id)
    assert body["name"] == product.name


@pytest.mark.api
def test_get_product_by_id_not_found(client, mock_product_service):
    mock_product_service.get_product_by_id.side_effect = ProductNotFoundException()

    response = client.get(f"/products/{uuid.uuid4()}")

    assert response.status_code == 404


@pytest.mark.api
def test_get_all_products(client, mock_product_service, product):
    mock_product_service.get_all_products.return_value = [product, product]

    response = client.get("/products")

    assert response.status_code == 200

    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == str(product.id)


@pytest.mark.api
def test_get_all_products_empty(client, mock_product_service):
    mock_product_service.get_all_products.return_value = []

    response = client.get("/products")

    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.api
def test_get_products_by_category_id(client, mock_product_service, product):
    mock_product_service.get_products_by_category_id.return_value = [product]

    response = client.get(f"/products/category/{product.category_id}")

    assert response.status_code == 200

    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["category_id"] == str(product.category_id)


@pytest.mark.api
def test_update_product(admin_client, mock_product_service, product):
    mock_product_service.update_product.return_value = product

    response = admin_client.put(
        "/products",
        json={
            "id": str(product.id),
            "name": product.name,
            "price": product.price,
            "description": product.description,
            "category_id": str(product.category_id),
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["id"] == str(product.id)
    assert body["name"] == product.name


@pytest.mark.api
def test_update_product_not_found(admin_client, mock_product_service):
    mock_product_service.update_product.side_effect = ProductNotFoundException()

    response = admin_client.put(
        "/products",
        json={
            "id": str(uuid.uuid4()),
            "name": "Notebook Gamer",
            "price": 4999.90,
            "description": "Descrição válida",
            "category_id": str(uuid.uuid4()),
        },
    )

    assert response.status_code == 404


@pytest.mark.api
def test_delete_product(admin_client, mock_product_service, product):
    mock_product_service.delete_product_by_id.return_value = True

    response = admin_client.delete(f"/products/{product.id}")

    assert response.status_code == 204
    mock_product_service.delete_product_by_id.assert_awaited_once_with(product.id)


@pytest.mark.api
def test_delete_product_not_found(admin_client, mock_product_service):
    mock_product_service.delete_product_by_id.side_effect = ProductNotFoundException()

    response = admin_client.delete(f"/products/{uuid.uuid4()}")

    assert response.status_code == 404
