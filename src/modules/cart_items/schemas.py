import uuid

from pydantic import BaseModel, Field


class BaseCartItemSchema(BaseModel):
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(gt=0)


class CreateCartItemSchema(BaseCartItemSchema):
    pass


class UpdateCartItemSchema(BaseCartItemSchema):
    id: uuid.UUID


class CartItemResponseSchema(BaseCartItemSchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}
