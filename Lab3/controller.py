from model import MenuItem, Restaurant, Order, Table
import oorms
from constants import MENU_ITEMS, FoodItem, SeatNumber
from typing import override


class Controller:
    """
    Do not modify this class, just its subclasses. Represents common behaviour of all
    Controllers. Python has a mechanism for explicitly dealing with abstract classes,
    which we haven't seen yet; raising RuntimeError gives a similar effect.
    """

    def __init__(self, view: oorms.ServerView, restaurant: Restaurant):
        self.view: oorms.ServerView = view
        self.restaurant: Restaurant = restaurant

    def add_item(self, menu_item: MenuItem) -> None:
        raise RuntimeError("add_item: some subclasses must implement")

    def cancel(self) -> None:
        raise RuntimeError("cancel: some subclasses must implement")

    def create_ui(self) -> None:
        raise RuntimeError("create_ui: all subclasses must implement")

    def done(self) -> None:
        raise RuntimeError("done: some subclasses must implement")

    def place_order(self) -> None:
        raise RuntimeError("place_order: some subclasses must implement")

    def seat_touched(self, seat_number: SeatNumber) -> None:
        raise RuntimeError("seat_touched: some subclasses must implement")

    def table_touched(self, table_index: int) -> None:
        raise RuntimeError("table_touched: some subclasses must implement")


class RestaurantController(Controller):
    """
    Restaurant Controller

    """

    @override
    def create_ui(self):
        self.view.create_restaurant_ui()

    @override
    def table_touched(self, table_index: int):
        table = self.restaurant.tables[table_index]
        self.view.set_controller(TableController(self.view, self.restaurant, table))


class TableController(Controller):
    """
    Table Controller

    """

    def __init__(self, view: oorms.ServerView, restaurant: Restaurant, table: Table):
        super().__init__(view, restaurant)
        self.table: Table = table

    @override
    def create_ui(self):
        self.view.create_table_ui(self.table)

    @override
    def seat_touched(self, seat_number: SeatNumber):
        oc = OrderController(self.view, self.restaurant, self.table, seat_number)
        self.view.set_controller(oc)

    @override
    def done(self):
        rc = RestaurantController(self.view, self.restaurant)
        self.view.set_controller(rc)


class OrderController(Controller):
    """
    Order Controller

    """

    def __init__(
        self,
        view: oorms.ServerView,
        restaurant: Restaurant,
        table: Table,
        seat_number: SeatNumber,
    ):
        super().__init__(view, restaurant)
        self.table = table
        self.seat_number = seat_number
        self.order: Order = self.table.order_for(seat_number)
        self.create_ui()

    @override
    def create_ui(self) -> None:
        self.view.create_order_ui(self.order)

    @override
    def add_item(self, menu_item: MenuItem) -> None:
        self.order.add_item(menu_item)
        self.create_ui()

    def update_order(self) -> None:
        self.order.place_new_orders()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )

    @override
    def cancel(self) -> None:
        self.order.remove_unordered_items()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
