from tkinter import Frame
from typing import override
from controllers import OrderController
from models import Order
from mvc import MVCFactory, ViewRouter
from views import OrderView


class OrderViewFactory(MVCFactory[OrderView, Order, OrderController]):
    def __init__(self, navigation: ViewRouter):
        super().__init__(navigation)

    @override
    def build_model(self) -> Order:
        raise Exception("Requires Order Payload!")

    @override
    def build_view(self, parent: Frame, model: Order) -> OrderView:
        return OrderView(parent, model)

    @override
    def build_controller(
        self, view: OrderView, model: Order, navigation: ViewRouter
    ) -> OrderController:
        return OrderController(view, model, navigation)
