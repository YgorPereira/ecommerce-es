import uuid

from pydantic import BaseModel, Field


class BaseCategorySchema(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=1, max_length=255)


class CreateCategorySchema(BaseCategorySchema):
    pass


class UpdateCategorySchema(BaseCategorySchema):
    id: uuid.UUID


class CategoryResponseSchema(BaseCategorySchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}
