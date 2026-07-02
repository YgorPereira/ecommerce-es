from src.shared.exceptions import NotFoundException


class OrderItemNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Item do pedido não encontrado")
