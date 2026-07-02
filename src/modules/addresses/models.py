import uuid

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class AddressModel(Base, IdMixin):
    __tablename__ = "addresses"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    address_line: Mapped[str] = mapped_column(String(255))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    number: Mapped[int] = mapped_column(Integer)
    district: Mapped[str] = mapped_column(String(100))
    complement: Mapped[str] = mapped_column(String(255))
