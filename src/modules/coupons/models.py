from datetime import datetime

from sqlalchemy import DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base
from src.database.idmixin import IdMixin


class CouponModel(Base, IdMixin):
    __tablename__ = "coupons"

    discount_percentage: Mapped[float] = mapped_column(Float)
    discount_amount: Mapped[float] = mapped_column(Float)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    usage_limit: Mapped[int] = mapped_column(Integer)
