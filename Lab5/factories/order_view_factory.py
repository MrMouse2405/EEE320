"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

OrderViewFactory:
    Factory for constructing order-related MVC components.
"""

from tkinter import Frame
from typing import override

from controllers import OrderController
from models import Order
from mvc import MVCFactory, ViewRouter
from views import OrderView


class OrderViewFactory(MVCFactory[OrderView, Order, OrderController]):
    """
    Builds and connects the model, view, and controller for an order view.
    """

    def __init__(self, navigation: ViewRouter) -> None:
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
