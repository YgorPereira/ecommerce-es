import uuid

from pydantic import BaseModel


class LoginInput(BaseModel):
    email: str
    password: str


class TokenOutput(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: uuid.UUID
