from __future__ import annotations
from typing import TYPE_CHECKING
from models import MenuItem, Order, OrderItem
from mvc import Controller, ViewRouter

if TYPE_CHECKING:
    from views import OrderView


class OrderController(Controller["OrderView", Order]):
    def __init__(self, view: "OrderView", model: Order, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def cancel_changes(self) -> None:
        self.model.remove_requested_item()
        self.navigation.go_back()

    def update_order(self) -> None:
        self.model.place_new_orders()
        self.navigation.go_back()

    def add_item(self, menu_item: MenuItem) -> None:
        self.model.add_item(menu_item)

    def remove(self, menu_item: OrderItem) -> None:
        self.model.remove_item(menu_item)
