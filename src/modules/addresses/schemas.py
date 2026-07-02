import uuid

from pydantic import BaseModel, Field


class BaseAddressSchema(BaseModel):
    user_id: uuid.UUID
    address_line: str = Field(min_length=1, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    number: int = Field(gt=0)
    district: str = Field(min_length=1, max_length=100)
    complement: str = Field(min_length=0, max_length=255)


class CreateAddressSchema(BaseAddressSchema):
    pass


class UpdateAddressSchema(BaseAddressSchema):
    id: uuid.UUID


class AddressResponseSchema(BaseAddressSchema):
    id: uuid.UUID

    model_config = {"from_attributes": True}
