from src.modules.coupons.entity import Coupon
from src.modules.coupons.models import CouponModel
from src.modules.coupons.schemas import CreateCouponSchema


class CouponMapper:

    @staticmethod
    def to_model(entity: Coupon) -> CouponModel:
        return CouponModel(
            id=entity.id,
            discount_percentage=entity.discount_percentage,
            discount_amount=entity.discount_amount,
            expires_at=entity.expires_at,
            usage_limit=entity.usage_limit,
        )

    @staticmethod
    def to_entity(model: CouponModel) -> Coupon:
        return Coupon(
            id=model.id,
            discount_percentage=model.discount_percentage,
            discount_amount=model.discount_amount,
            expires_at=model.expires_at,
            usage_limit=model.usage_limit,
        )

    @staticmethod
    def from_create_schema(schema: CreateCouponSchema) -> Coupon:
        return Coupon(
            discount_percentage=schema.discount_percentage,
            discount_amount=schema.discount_amount,
            expires_at=schema.expires_at,
            usage_limit=schema.usage_limit,
        )
