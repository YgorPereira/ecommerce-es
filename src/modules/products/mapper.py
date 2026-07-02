from src.modules.products.entity import Product
from src.modules.products.models import ProductModel
from src.modules.products.schemas import CreateProductSchema


class ProductMapper:

    @staticmethod
    def to_model(entity: Product) -> ProductModel:
        return ProductModel(
            id=entity.id,
            name=entity.name,
            price=entity.price,
            description=entity.description,
            category_id=entity.category_id,
        )

    @staticmethod
    def to_entity(model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            price=model.price,
            description=model.description,
            category_id=model.category_id,
        )

    @staticmethod
    def from_create_schema(schema: CreateProductSchema) -> Product:
        return Product(
            name=schema.name,
            price=schema.price,
            description=schema.description,
            category_id=schema.category_id,
        )
