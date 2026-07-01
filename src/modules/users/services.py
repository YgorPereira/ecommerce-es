from typing import List
import uuid

from src.core.security import hash_password
from src.modules.users.entity import User
from src.modules.users.exceptions import (
    UserEmailAlreadyExistsException,
    UserNotFoundException,
)
from src.modules.users.mapper import UserMapper
from src.modules.users.repository import UserRepository
from src.modules.users.schemas import CreateUserSchema, UpdateUserSchema


class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, user: CreateUserSchema) -> User:
        db_item = await self.repository.get_by_email(user.email)

        if db_item is not None:
            raise UserEmailAlreadyExistsException()
        
        hashed = hash_password(user.password) 
        user.password = hashed

        return await self.repository.create(UserMapper.from_create_schema(user))

    async def get_all_users(self) -> List[User]:
        return await self.repository.get_all()

    async def get_user_by_id(self, id: uuid.UUID) -> User | None:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise UserNotFoundException()

        return db_item

    async def get_user_by_email(self, email: str) -> User | None:
        db_item = await self.repository.get_by_email(email)

        if db_item is None:
            raise UserNotFoundException()

        return db_item

    async def update_user(self, user: UpdateUserSchema) -> User | None:
        db_item = await self.repository.get_by_id(user.id)

        if db_item is None:
            raise UserNotFoundException()

        return await self.repository.update_by_id(user)

    async def delete_user_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise UserNotFoundException()

        return await self.repository.delete_by_id(id)
