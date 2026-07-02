from src.shared.exceptions import ConflictException, NotFoundException


class OrderNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Pedido não encontrado")


class OrderAlreadyPaidException(ConflictException):
    def __init__(self):
        super().__init__("Pedido já pago não pode ser alterado")
