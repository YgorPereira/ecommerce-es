from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.categories.repository import CategoryRepository
from src.modules.categories.schemas import (
    CreateCategorySchema,
    UpdateCategorySchema,
    CategoryResponseSchema,
)
from src.modules.categories.services import CategoryService

category_router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


def get_category_service(
    db: Session = Depends(get_db),
) -> CategoryService:
    repository = CategoryRepository(db)
    return CategoryService(repository)


@category_router.post(
    "",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    category: CreateCategorySchema,
    service: CategoryService = Depends(get_category_service),
):
    return await service.create_category(category)


@category_router.get(
    "",
    response_model=List[CategoryResponseSchema],
)
async def get_all_categories(
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_all_categories()


@category_router.get(
    "/{category_id}",
    response_model=CategoryResponseSchema,
)
async def get_category_by_id(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    return await service.get_category_by_id(category_id)


@category_router.put(
    "",
    response_model=CategoryResponseSchema,
)
async def update_category(
    category: UpdateCategorySchema,
    service: CategoryService = Depends(get_category_service),
):
    return await service.update_category(category)


@category_router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: UUID,
    service: CategoryService = Depends(get_category_service),
):
    await service.delete_category_by_id(category_id)
