"""
Provides the controller layer for the OORMS system.

Submitting lab group: Syed, Pabon
Submission date: Nov 5, 2025

Original code by EEE320 instructors.
"""

from __future__ import annotations
from typing import override
import oorms
from model import MenuItem, OrderItem, Restaurant, Table, Order
from abc import ABC, abstractmethod

type RestaurantView = oorms.RestaurantView
type Printer = oorms.Printer


class Controller(ABC):
    def __init__(self, view: RestaurantView, restaurant: Restaurant) -> None:
        self.view: RestaurantView = view
        self.restaurant: Restaurant = restaurant

    @abstractmethod
    def create_ui(self) -> None:
        pass


class RestaurantController(Controller):
    @override
    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number: int) -> None:
        self.view.set_controller(
            TableController(
                self.view, self.restaurant, self.restaurant.tables[table_number]
            )
        )
        self.view.update()


class TableController(Controller):
    def __init__(
        self, view: RestaurantView, restaurant: Restaurant, table: Table
    ) -> None:
        super().__init__(view, restaurant)
        self.table: Table = table

    def create_ui(self) -> None:
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number: int) -> None:
        self.view.set_controller(
            OrderController(self.view, self.restaurant, self.table, seat_number)
        )
        self.view.update()

    def make_bills(self, printer: Printer) -> None:
        # TODO: switch to appropriate controller & UI so server can create and print bills
        # for this table. The following line illustrates how bill printing works, but the
        # actual printing should happen in the (new) controller, not here.
        printer.print(
            f"Set up bills for table {self.restaurant.tables.index(self.table)}"
        )

    def done(self) -> None:
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):
    def __init__(
        self,
        view: RestaurantView,
        restaurant: Restaurant,
        table: Table,
        seat_number: int,
    ) -> None:
        super().__init__(view, restaurant)
        self.table: Table = table
        self.order: Order = self.table.order_for(seat_number)

    def create_ui(self) -> None:
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item: MenuItem) -> None:
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item: OrderItem) -> None:
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self) -> None:
        self.order.place_new_orders()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
        self.restaurant.notify_views()

    def cancel_changes(self) -> None:
        self.order.remove_unordered_items()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
        self.restaurant.notify_views()
