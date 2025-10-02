from typing import override
from constants import SeatNumber
from abc import ABC
import oorms
import model

type View = oorms.ServerView | oorms.KitchenView


class Controller(ABC):
    def __init__(self, view: View, restaurant: model.Restaurant):
        self.view: View = view
        self.restaurant: model.Restaurant = restaurant

    def create_ui(self) -> None:
        pass


class RestaurantController(Controller):
    @override
    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number: int):
        self.view.set_controller(
            TableController(
                self.view, self.restaurant, self.restaurant.tables[table_number]
            )
        )
        self.view.update()


class TableController(Controller):
    def __init__(self, view: View, restaurant: model.Restaurant, table: model.Table):
        super().__init__(view, restaurant)
        self.table: model.Table = table

    @override
    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number: SeatNumber):
        self.view.set_controller(
            OrderController(self.view, self.restaurant, self.table, seat_number)
        )
        self.view.update()

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class OrderController(Controller):
    def __init__(
        self,
        view: View,
        restaurant: model.Restaurant,
        table: model.Table,
        seat_number: SeatNumber,
    ):
        super().__init__(view, restaurant)
        self.table: model.Table = table
        self.order: model.Order = self.table.order_for(seat_number)

    @override
    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item: model.MenuItem):
        self.order.add_item(menu_item)
        self.view.update()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
        self.restaurant.notify_views()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
        self.restaurant.notify_views()


class KitchenController(Controller):
    @override
    def create_ui(self):
        self.view.create_kitchen_order_ui()

    # TODO: implement a method to handle button presses on the KitchenView
