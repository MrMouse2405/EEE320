from tkinter import Frame
from typing import override
from controllers.OrderController import OrderController
from models import Order
from mvc import MVCFactory, ViewRouter
from repositories import MenuItemRepository
from views.OrderView import OrderView

__menu_item_repository = MenuItemRepository()


class OrderViewFactory(MVCFactory[OrderView, Order, OrderController]):
    def __init__(self, model: Order, navigation: ViewRouter):
        super().__init__(navigation)
        self._model: Order = model

    @override
    def build_model(self) -> Order:
        return self._model

    @override
    def build_view(self, parent: Frame, model: Order) -> OrderView:
        return OrderView(parent, model)

    @override
    def build_controller(
        self, view: OrderView, model: Order, navigation: ViewRouter
    ) -> OrderController:
        return OrderController(view, model, navigation)
