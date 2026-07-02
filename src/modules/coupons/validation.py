from datetime import datetime

from src.modules.coupons.entity import Coupon
from src.modules.coupons.exceptions import (
    CouponExpiredException,
    CouponUsageLimitReachedException,
)


def assert_coupon_applicable(coupon: Coupon, now: datetime) -> None:
    """Garante que o cupom pode ser aplicado ou levanta a exceção adequada.

    Regra de negócio: cupons só podem ser usados enquanto ativos (com usos
    disponíveis) e dentro da validade.
    """
    if coupon.usage_limit <= 0:
        raise CouponUsageLimitReachedException()

    if coupon.expires_at <= now:
        raise CouponExpiredException()
