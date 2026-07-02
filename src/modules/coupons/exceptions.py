from src.shared.exceptions import ConflictException, NotFoundException


class CouponNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Cupom não encontrado")


class CouponExpiredException(ConflictException):
    def __init__(self):
        super().__init__("Cupom expirado")


class CouponUsageLimitReachedException(ConflictException):
    def __init__(self):
        super().__init__("Cupom sem usos disponíveis")
