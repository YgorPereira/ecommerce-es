import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BaseOrderSchema(BaseModel):
    user_id: uuid.UUID
    address_id: uuid.UUID
    coupon_id: uuid.UUID | None = None
    total_amount: float = Field(ge=0)


class CreateOrderSchema(BaseOrderSchema):
    pass


class UpdateOrderSchema(BaseOrderSchema):
    id: uuid.UUID
    status: str = Field(min_length=1, max_length=50)


class OrderResponseSchema(BaseOrderSchema):
    id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}
