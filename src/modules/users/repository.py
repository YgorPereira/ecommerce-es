from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.modules.users.entity import User
from src.modules.users.mapper import UserMapper
from src.modules.users.models import UserModel


class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, user: User) -> User:
        mapped_user = UserMapper.to_model(user)
        self.db_session.add(mapped_user)
        self.db_session.flush()
        self.db_session.refresh(mapped_user)
        return UserMapper.to_entity(mapped_user)

    def get_all(self) -> List[User]:
        query = select(UserModel)
        models = list(self.db_session.scalars(query).all())

        return [UserMapper.to_entity(model) for model in models]

    def get_by_id(self, id: uuid.UUID) -> UserModel | None:
        model = self.db_session.get(UserModel, id)

        if model is None:
            return None

        return UserMapper.to_entity(model)

    def get_by_email(self, email: str) -> User | None :
        query = select(UserModel).where(UserModel.email == email)

        model = self.db_session.scalars(query).first()
        
        if model is None:
            return None
        
        return UserMapper.to_entity(model)

    def update_by_id(self, user: User) -> UserModel | None:
        model = UserMapper.to_model(user)
        db_user = self.db_session.merge(model)

        if db_user is None: 
            return None

        self.db_session.flush()

        return UserMapper.to_entity(db_user)

    def delete_by_id(self, id: uuid.UUID) -> bool:
        model = self.db_session.get(UserModel, id)

        if model is None:
            return False

        self.db_session.delete(model)
        self.db_session.flush()
        return True
