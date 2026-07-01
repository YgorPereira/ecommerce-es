from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin
from src.modules.users.enums.role import UserRole


class UserModel(Base, IdMixin):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(100))
    cpf: Mapped[str] = mapped_column(String(11), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.COMMON)
