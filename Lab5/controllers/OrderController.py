from __future__ import annotations
from models import MenuItem, Order, OrderItem
from mvc import Controller, ViewRouter
from views import OrderView


class OrderController(Controller[OrderView, Order]):
    def __init__(self, view: OrderView, model: Order, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def cancel_changes(self):
        print("cancel changes!")

    def update_order(self):
        print("update order!")

    def add_item(self, menu_item: MenuItem):
        print("add item", menu_item)

    def remove(self, menu_item: OrderItem) -> None:
        print("remove item", menu_item)
