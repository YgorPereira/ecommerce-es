from src.shared.exceptions import NotFoundException


class OrderNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Pedido não encontrado")
