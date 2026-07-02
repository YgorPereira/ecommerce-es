import uuid
from datetime import datetime

from pydantic import BaseModel


class BaseCartSchema(BaseModel):
    user_id: uuid.UUID
    coupon_id: uuid.UUID | None = None


class CreateCartSchema(BaseCartSchema):
    pass


class UpdateCartSchema(BaseCartSchema):
    id: uuid.UUID


class CartResponseSchema(BaseCartSchema):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class CheckoutSchema(BaseModel):
    address_id: uuid.UUID
