from typing import List
import uuid

from src.modules.categories.entity import Category
from src.modules.categories.exceptions import (
    CategoryNameAlreadyExistsException,
    CategoryNotFoundException,
)
from src.modules.categories.mapper import CategoryMapper
from src.modules.categories.repository import CategoryRepository
from src.modules.categories.schemas import (
    CreateCategorySchema,
    UpdateCategorySchema,
)


class CategoryService:
    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def create_category(self, category: CreateCategorySchema) -> Category:
        db_item = await self.repository.get_by_name(category.name)

        if db_item is not None:
            raise CategoryNameAlreadyExistsException()

        return await self.repository.create(CategoryMapper.from_create_schema(category))

    async def get_all_categories(self) -> List[Category]:
        return await self.repository.get_all()

    async def get_category_by_id(self, id: uuid.UUID) -> Category:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CategoryNotFoundException()

        return db_item

    async def update_category(self, category: UpdateCategorySchema) -> Category | None:
        db_item = await self.repository.get_by_id(category.id)

        if db_item is None:
            raise CategoryNotFoundException()

        existing = await self.repository.get_by_name(category.name)

        if existing is not None and existing.id != category.id:
            raise CategoryNameAlreadyExistsException()

        return await self.repository.update_by_id(
            Category(
                id=category.id,
                name=category.name,
                description=category.description,
            )
        )

    async def delete_category_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CategoryNotFoundException()

        return await self.repository.delete_by_id(id)
