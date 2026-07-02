from typing import List
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.coupons.entity import Coupon
from src.modules.coupons.mapper import CouponMapper
from src.modules.coupons.models import CouponModel


class CouponRepository:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create(self, coupon: Coupon) -> Coupon:
        mapped_coupon = CouponMapper.to_model(coupon)
        self.db_session.add(mapped_coupon)
        await self.db_session.flush()
        await self.db_session.refresh(mapped_coupon)
        return CouponMapper.to_entity(mapped_coupon)

    async def get_all(self) -> List[Coupon]:
        query = select(CouponModel)
        result = await self.db_session.scalars(query)
        models = result.all()

        return [CouponMapper.to_entity(model) for model in models]

    async def get_by_id(self, id: uuid.UUID) -> Coupon | None:
        model = await self.db_session.get(CouponModel, id)

        if model is None:
            return None

        return CouponMapper.to_entity(model)

    async def update_by_id(self, coupon: Coupon) -> Coupon | None:
        model = CouponMapper.to_model(coupon)
        db_coupon = await self.db_session.merge(model)

        if db_coupon is None:
            return None

        await self.db_session.flush()

        return CouponMapper.to_entity(db_coupon)

    async def delete_by_id(self, id: uuid.UUID) -> bool:
        model = await self.db_session.get(CouponModel, id)

        if model is None:
            return False

        await self.db_session.delete(model)
        await self.db_session.flush()
        return True
