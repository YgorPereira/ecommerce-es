from typing import List
import uuid

from src.modules.products.entity import Product
from src.modules.products.exceptions import ProductNotFoundException
from src.modules.products.mapper import ProductMapper
from src.modules.products.repository import ProductRepository
from src.modules.products.schemas import CreateProductSchema, UpdateProductSchema


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def create_product(self, product: CreateProductSchema) -> Product:
        return await self.repository.create(ProductMapper.from_create_schema(product))

    async def get_all_products(self) -> List[Product]:
        return await self.repository.get_all()

    async def get_product_by_id(self, id: uuid.UUID) -> Product:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise ProductNotFoundException()

        return db_item

    async def get_products_by_category_id(self, category_id: uuid.UUID) -> List[Product]:
        return await self.repository.get_by_category_id(category_id)

    async def update_product(self, product: UpdateProductSchema) -> Product | None:
        db_item = await self.repository.get_by_id(product.id)

        if db_item is None:
            raise ProductNotFoundException()

        return await self.repository.update_by_id(product)

    async def delete_product_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise ProductNotFoundException()

        return await self.repository.delete_by_id(id)