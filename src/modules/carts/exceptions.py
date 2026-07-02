from src.shared.exceptions import NotFoundException


class CartNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Carrinho não encontrado")
