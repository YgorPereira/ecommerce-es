from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.users.entity import User
from src.modules.users.mapper import UserMapper
from src.modules.users.models import UserModel


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, user: User) -> User:
        mapped_user = UserMapper.to_model(user)
        self.db_session.add(mapped_user)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_user)
        return UserMapper.to_entity(mapped_user)

    async def get_all(self) -> List[User]:
        query = select(UserModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [UserMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> UserModel | None:
        model = await self.db_session.get(UserModel, id)

        if model is None:
            return None

        return UserMapper.to_entity(model)

    async def get_by_email(self, email: str) -> User | None:
        query = select(UserModel).where(UserModel.email == email)

        result = await self.db_session.scalars(query)
        model = result.first()

        if model is None:
            return None

        return UserMapper.to_entity(model)

    async def update_by_id(self, user: User) -> User | None:
        model = UserMapper.to_model(user)
        db_user = await self.db_session.merge(model)

        if db_user is None:
            return None

        await self.db_session.flush()

        return UserMapper.to_entity(db_user)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(UserModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
