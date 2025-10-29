from __future__ import annotations
from models import Order
from mvc import Controller
from views import OrderView


class OrderController(Controller[OrderView, Order]):
    def __init__(self, view: OrderView, model: Order) -> None:
        super().__init__(view, model)
