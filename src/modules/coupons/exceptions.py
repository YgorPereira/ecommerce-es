from src.shared.exceptions import NotFoundException


class CouponNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Cupom não encontrado")
