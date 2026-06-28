import uuid

from pydantic import BaseModel, EmailStr, Field

from src.modules.users.enums.role import UserRole


class BaseUserSchema(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    email: EmailStr
    role: UserRole


class CreateUserSchema(BaseUserSchema):
    cpf: str = Field(min_length=11, max_length=11)
    password: str = Field(min_length=8)


class UpdateUserSchema(BaseUserSchema):
    id: uuid.UUID