import re
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator

from src.modules.users.enums.role import UserRole


class BaseUserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    role: UserRole


class CreateUserSchema(BaseUserSchema):
    cpf: str = Field(min_length=11, max_length=14)
    password: str = Field(min_length=8)

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value: str) -> str:
        digits = re.sub(r"\D", "", value)

        if len(digits) != 11:
            raise ValueError("CPF deve conter 11 dígitos")

        if len(set(digits)) == 1:
            raise ValueError("CPF inválido")

        total = sum(int(d) * (10 - i) for i, d in enumerate(digits[:9]))
        remainder = (total * 10) % 11
        if remainder == 10:
            remainder = 0
        if remainder != int(digits[9]):
            raise ValueError("CPF inválido")

        total = sum(int(d) * (11 - i) for i, d in enumerate(digits[:10]))
        remainder = (total * 10) % 11
        if remainder == 10:
            remainder = 0
        if remainder != int(digits[10]):
            raise ValueError("CPF inválido")

        return digits


class UpdateUserSchema(BaseUserSchema):
    id: uuid.UUID


class UserResponseSchema(BaseUserSchema):
    id: uuid.UUID
    cpf: str

    model_config = {"from_attributes": True}
