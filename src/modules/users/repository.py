from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.modules.users.models import UserModel


class UserRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create(self, user: UserModel) -> UserModel:
        self.db_session.add(user)
        self.db_session.flush()
        self.db_session.refresh(user)
        return user

    def get_all(self) -> List[UserModel]:
        query = select(UserModel)
        return list(self.db_session.scalars(query).all())

    def get_by_id(self, id: uuid.UUID) -> UserModel | None:
        return self.db_session.get(UserModel, id)

    def get_by_email(self, email: str):
        query = select(UserModel).where(UserModel.email == email)
        return self.db_session.scalars(query).first()

    def update_by_id(self, user: UserModel) -> UserModel | None:
        db_user = self.db_session.merge(user)

        self.db_session.flush()

        return db_user

    def delete_by_id(self, id: uuid.UUID) -> bool:
        user = self.get_by_id(id)

        if not user:
            return False

        self.db_session.delete(user)
        self.db_session.flush()
        return True
