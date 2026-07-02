from src.shared.exceptions import NotFoundException


class CartItemNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__("Item do carrinho não encontrado")
