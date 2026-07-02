import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BaseInventorySchema(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(ge=0)


class CreateInventorySchema(BaseInventorySchema):
    pass


class UpdateInventorySchema(BaseInventorySchema):
    id: uuid.UUID


class InventoryResponseSchema(BaseInventorySchema):
    id: uuid.UUID
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReserveStockSchema(BaseModel):
    quantity: int = Field(gt=0)
