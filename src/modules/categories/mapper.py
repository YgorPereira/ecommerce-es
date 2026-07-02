from src.modules.categories.entity import Category
from src.modules.categories.models import CategoryModel
from src.modules.categories.schemas import CreateCategorySchema


class CategoryMapper:

    @staticmethod
    def to_model(entity: Category) -> CategoryModel:
        return CategoryModel(
            id=entity.id,
            name=entity.name,
            description=entity.description,
        )

    @staticmethod
    def to_entity(model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            description=model.description,
        )

    @staticmethod
    def from_create_schema(schema: CreateCategorySchema) -> Category:
        return Category(
            name=schema.name,
            description=schema.description,
        )
