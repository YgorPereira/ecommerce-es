"""Cálculo de total do pedido (subtotal dos itens + desconto do cupom).

Função pura, sem I/O — recebe os itens e um cupom opcional (já validado) e
devolve o total. Isolar o cálculo aqui garante precisão e testabilidade.
"""

from dataclasses import dataclass

from src.modules.coupons.entity import Coupon


@dataclass
class LineItem:
    price: float
    quantity: int


def calculate_subtotal(items: list[LineItem]) -> float:
    return sum(item.price * item.quantity for item in items)


def calculate_total(items: list[LineItem], coupon: Coupon | None = None) -> float:
    subtotal = calculate_subtotal(items)

    if coupon is not None:
        subtotal = coupon.apply_to(subtotal)

    return round(subtotal, 2)
