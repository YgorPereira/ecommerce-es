import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BasePaymentSchema(BaseModel):
    order_id: uuid.UUID
    amount: float = Field(ge=0)
    method: str = Field(min_length=1, max_length=50)


class CreatePaymentSchema(BasePaymentSchema):
    pass


class UpdatePaymentSchema(BasePaymentSchema):
    id: uuid.UUID
    status: str = Field(min_length=1, max_length=50)
    gateway_reference: str | None = None


class PaymentResponseSchema(BasePaymentSchema):
    id: uuid.UUID
    status: str
    gateway_reference: str | None
    processed_at: datetime | None

    model_config = {"from_attributes": True}


class PaymentWebhookSchema(BaseModel):
    reference: str = Field(min_length=1)
    status: str = Field(min_length=1)
