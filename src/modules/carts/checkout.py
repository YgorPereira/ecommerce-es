"""Checkout transacional: transforma um carrinho em pedido.

Tudo roda dentro da mesma transação do request (ver ``get_db``): a reserva de
estoque de cada item, o cálculo do total e a criação do pedido/itens. Se
qualquer passo falhar (ex.: estoque insuficiente), a transação inteira sofre
rollback — nada é reservado ou cobrado pela metade.
"""

from datetime import datetime, timezone
import uuid

from src.modules.cart_items.repository import CartItemRepository
from src.modules.carts.exceptions import CartNotFoundException, EmptyCartException
from src.modules.carts.repository import CartRepository
from src.modules.coupons.exceptions import CouponNotFoundException
from src.modules.coupons.repository import CouponRepository
from src.modules.coupons.validation import assert_coupon_applicable
from src.modules.inventories.exceptions import InsufficientStockException
from src.modules.inventories.repository import InventoryRepository
from src.modules.order_items.entity import OrderItem
from src.modules.order_items.repository import OrderItemRepository
from src.modules.orders.entity import Order
from src.modules.orders.pricing import LineItem, calculate_total
from src.modules.orders.repository import OrderRepository
from src.modules.orders.services import DEFAULT_ORDER_STATUS
from src.modules.products.exceptions import ProductNotFoundException
from src.modules.products.repository import ProductRepository


class CheckoutService:
    def __init__(
        self,
        cart_repository: CartRepository,
        cart_item_repository: CartItemRepository,
        product_repository: ProductRepository,
        inventory_repository: InventoryRepository,
        coupon_repository: CouponRepository,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
    ):
        self.cart_repository = cart_repository
        self.cart_item_repository = cart_item_repository
        self.product_repository = product_repository
        self.inventory_repository = inventory_repository
        self.coupon_repository = coupon_repository
        self.order_repository = order_repository
        self.order_item_repository = order_item_repository

    async def checkout(self, cart_id: uuid.UUID, address_id: uuid.UUID) -> Order:
        cart = await self.cart_repository.get_by_id(cart_id)

        if cart is None:
            raise CartNotFoundException()

        items = await self.cart_item_repository.get_by_cart_id(cart_id)

        if not items:
            raise EmptyCartException()

        # Reserva atômica do estoque de cada item. Se algum falhar, a exceção
        # propaga e o request inteiro faz rollback (nada fica reservado).
        reserved: list[tuple] = []
        for item in items:
            product = await self.product_repository.get_by_id(item.product_id)

            if product is None:
                raise ProductNotFoundException()

            ok = await self.inventory_repository.decrement(
                item.product_id, item.quantity
            )

            if not ok:
                raise InsufficientStockException()

            reserved.append((item, product))

        coupon = None
        if cart.coupon_id is not None:
            coupon = await self.coupon_repository.get_by_id(cart.coupon_id)

            if coupon is None:
                raise CouponNotFoundException()

            assert_coupon_applicable(coupon, datetime.now(timezone.utc))

        line_items = [
            LineItem(price=product.price, quantity=item.quantity)
            for item, product in reserved
        ]
        total = calculate_total(line_items, coupon)

        order = await self.order_repository.create(
            Order(
                user_id=cart.user_id,
                address_id=address_id,
                coupon_id=cart.coupon_id,
                total_amount=total,
                status=DEFAULT_ORDER_STATUS,
                created_at=datetime.now(timezone.utc),
            )
        )

        for item, product in reserved:
            await self.order_item_repository.create(
                OrderItem(
                    order_id=order.id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    price=product.price,
                )
            )

        return order
