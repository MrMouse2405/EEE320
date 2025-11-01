"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

OrderController:
    Handles menu selection, order updates, and cancellation actions.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from mvc import Controller, ViewRouter
from models import MenuItem, Order, OrderItem

if TYPE_CHECKING:
    from views import OrderView


class OrderController(Controller["OrderView", Order]):
    """
    Manages item selection, removal, and order state updates for a single seat.
    """

    def __init__(self, view: "OrderView", model: Order, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def cancel_changes(self) -> None:
        self.model.remove_requested_items()
        self.navigation.go_back()

    def update_order(self) -> None:
        self.model.place_new_orders()
        self.navigation.go_back()

    def add_item(self, menu_item: MenuItem) -> None:
        self.model.add_item(menu_item)

    def remove(self, menu_item: OrderItem) -> None:
        self.model.remove_item(menu_item)
