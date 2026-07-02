from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.database.session import get_db
from src.modules.auth.permissions import require_admin
from src.modules.users.entity import User
from src.modules.coupons.repository import CouponRepository
from src.modules.coupons.schemas import (
    CreateCouponSchema,
    UpdateCouponSchema,
    CouponResponseSchema,
)
from src.modules.coupons.services import CouponService

coupon_router = APIRouter(
    prefix="/coupons",
    tags=["Coupons"],
)


def get_coupon_service(
    db: Session = Depends(get_db),
) -> CouponService:
    repository = CouponRepository(db)
    return CouponService(repository)


@coupon_router.post(
    "",
    response_model=CouponResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_coupon(
    coupon: CreateCouponSchema,
    service: CouponService = Depends(get_coupon_service),
    _: User = Depends(require_admin),
):
    return await service.create_coupon(coupon)


@coupon_router.get(
    "",
    response_model=List[CouponResponseSchema],
)
async def get_all_coupons(
    service: CouponService = Depends(get_coupon_service),
):
    return await service.get_all_coupons()


@coupon_router.get(
    "/{coupon_id}",
    response_model=CouponResponseSchema,
)
async def get_coupon_by_id(
    coupon_id: UUID,
    service: CouponService = Depends(get_coupon_service),
):
    return await service.get_coupon_by_id(coupon_id)


@coupon_router.put(
    "",
    response_model=CouponResponseSchema,
)
async def update_coupon(
    coupon: UpdateCouponSchema,
    service: CouponService = Depends(get_coupon_service),
    _: User = Depends(require_admin),
):
    return await service.update_coupon(coupon)


@coupon_router.delete(
    "/{coupon_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_coupon(
    coupon_id: UUID,
    service: CouponService = Depends(get_coupon_service),
    _: User = Depends(require_admin),
):
    await service.delete_coupon_by_id(coupon_id)
