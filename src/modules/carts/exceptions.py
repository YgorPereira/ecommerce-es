from src.shared.exceptions import AppException, NotFoundException


class CartNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Carrinho não encontrado")


class EmptyCartException(AppException):
    def __init__(self):
        super().__init__("Carrinho vazio", status_code=400)
