import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BaseCouponSchema(BaseModel):
    discount_percentage: float = Field(ge=0, le=100)
    discount_amount: float = Field(ge=0)
    expires_at: datetime
    usage_limit: int = Field(gt=0)


class CreateCouponSchema(BaseCouponSchema):
    pass


class UpdateCouponSchema(BaseCouponSchema):
    id: uuid.UUID


class CouponResponseSchema(BaseCouponSchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}
