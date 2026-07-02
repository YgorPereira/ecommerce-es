from typing import List
import uuid

from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import CouponNotFoundException
from src.modules.coupons.mapper import CouponMapper
from src.modules.coupons.repository import CouponRepository
from src.modules.coupons.schemas import CreateCouponSchema, UpdateCouponSchema


class CouponService:
    def __init__(self, repository: CouponRepository):
        self.repository = repository

    async def create_coupon(self, coupon: CreateCouponSchema) -> Coupon:
        return await self.repository.create(CouponMapper.from_create_schema(coupon))

    async def get_all_coupons(self) -> List[Coupon]:
        return await self.repository.get_all()

    async def get_coupon_by_id(self, id: uuid.UUID) -> Coupon:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CouponNotFoundException()

        return db_item

    async def update_coupon(self, coupon: UpdateCouponSchema) -> Coupon | None:
        db_item = await self.repository.get_by_id(coupon.id)

        if db_item is None:
            raise CouponNotFoundException()

        return await self.repository.update_by_id(
            Coupon(
                id=coupon.id,
                discount_percentage=coupon.discount_percentage,
                discount_amount=coupon.discount_amount,
                expires_at=coupon.expires_at,
                usage_limit=coupon.usage_limit,
            )
        )

    async def delete_coupon_by_id(self, id: uuid.UUID) -> bool:
        db_item = await self.repository.get_by_id(id)

        if db_item is None:
            raise CouponNotFoundException()

        return await self.repository.delete_by_id(id)
