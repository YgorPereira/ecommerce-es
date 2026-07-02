from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.products.repository import ProductRepository
from src.modules.products.schemas import (
    CreateProductSchema,
    UpdateProductSchema,
    ProductResponseSchema,
)
from src.modules.products.services import ProductService

product_router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


def get_product_service(
    db: Session = Depends(get_db),
) -> ProductService:
    repository = ProductRepository(db)
    return ProductService(repository)


@product_router.post(
    "",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    product: CreateProductSchema,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(product)


@product_router.get(
    "",
    response_model=List[ProductResponseSchema],
)
async def get_all_products(
    service: ProductService = Depends(get_product_service),
):
    return await service.get_all_products()


@product_router.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
)
async def get_product_by_id(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_product_by_id(product_id)


@product_router.get(
    "/category/{category_id}",
    response_model=List[ProductResponseSchema],
)
async def get_products_by_category_id(
    category_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    return await service.get_products_by_category_id(category_id)


@product_router.put(
    "",
    response_model=ProductResponseSchema,
)
async def update_product(
    product: UpdateProductSchema,
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(product)


@product_router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_product(
    product_id: UUID,
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product_by_id(product_id)
