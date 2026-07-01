from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.products.entity import Product
from src.modules.products.mapper import ProductMapper
from src.modules.products.models import ProductModel


class ProductRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, product: Product) -> Product:
        mapped_product = ProductMapper.to_model(product)
        self.db_session.add(mapped_product)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_product)
        return ProductMapper.to_entity(mapped_product)

    async def get_all(self) -> List[Product]:
        query = select(ProductModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [ProductMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Product | None:
        model = await self.db_session.get(ProductModel, id)

        if model is None:
            return None

        return ProductMapper.to_entity(model)

    async def get_by_category_id(self, category_id: uuid.UUID) -> List[Product]:
        query = select(ProductModel).where(ProductModel.category_id == category_id)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [ProductMapper.to_entity(model) for model in models]

    async def update_by_id(self, product: Product) -> Product | None:
        model = ProductMapper.to_model(product)
        db_product = await self.db_session.merge(model)

        if db_product is None:
            return None

        await self.db_session.flush()

        return ProductMapper.to_entity(db_product)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(ProductModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True