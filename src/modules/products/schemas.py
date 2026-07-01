import uuid

from pydantic import BaseModel, Field


class BaseProductSchema(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    price: float = Field(gt=0)
    description: str = Field(min_length=1, max_length=255)
    category_id: uuid.UUID


class CreateProductSchema(BaseProductSchema):
    pass


class UpdateProductSchema(BaseProductSchema):
    id: uuid.UUID


class ProductResponseSchema(BaseProductSchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}