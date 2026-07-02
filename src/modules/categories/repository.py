from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.categories.entity import Category
from src.modules.categories.mapper import CategoryMapper
from src.modules.categories.models import CategoryModel


class CategoryRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, category: Category) -> Category:
        mapped_category = CategoryMapper.to_model(category)
        self.db_session.add(mapped_category)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_category)
        return CategoryMapper.to_entity(mapped_category)

    async def get_all(self) -> List[Category]:
        query = select(CategoryModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CategoryMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Category | None:
        model = await self.db_session.get(CategoryModel, id)

        if model is None:
            return None

        return CategoryMapper.to_entity(model)

    async def get_by_name(self, name: str) -> Category | None:
        query = select(CategoryModel).where(CategoryModel.name == name)
        model = await self.db_session.scalar(query)

        if model is None:
            return None

        return CategoryMapper.to_entity(model)

    async def update_by_id(self, category: Category) -> Category | None:
        model = CategoryMapper.to_model(category)
        db_category = await self.db_session.merge(model)

        if db_category is None:
            return None

        await self.db_session.flush()

        return CategoryMapper.to_entity(db_category)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(CategoryModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
