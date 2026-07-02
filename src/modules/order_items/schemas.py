import uuid

from pydantic import BaseModel, Field


class BaseOrderItemSchema(BaseModel):
    order_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int = Field(gt=0)
    price: float = Field(ge=0)


class CreateOrderItemSchema(BaseOrderItemSchema):
    pass


class UpdateOrderItemSchema(BaseOrderItemSchema):
    id: uuid.UUID


class OrderItemResponseSchema(BaseOrderItemSchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}
