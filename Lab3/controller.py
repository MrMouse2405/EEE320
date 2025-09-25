from model import Restaurant, Order, Table
import oorms
from constants import FoodItem, SeatNumber


class Controller:
    """
    Do not modify this class, just its subclasses. Represents common behaviour of all
    Controllers. Python has a mechanism for explicitly dealing with abstract classes,
    which we haven't seen yet; raising RuntimeError gives a similar effect.
    """

    def __init__(self, view: oorms.ServerView, restaurant: Restaurant):
        self.view = view
        self.restaurant = restaurant

    def add_item(self, item: FoodItem):
        raise RuntimeError("add_item: some subclasses must implement")

    def cancel(self):
        raise RuntimeError("cancel: some subclasses must implement")

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def done(self):
        raise RuntimeError("done: some subclasses must implement")

    def place_order(self):
        raise RuntimeError("place_order: some subclasses must implement")

    def seat_touched(self, seat_number: SeatNumber):
        raise RuntimeError("seat_touched: some subclasses must implement")

    def table_touched(self, table_index: int):
        raise RuntimeError("table_touched: some subclasses must implement")


class RestaurantController(Controller):
    """
    Restaurant Controller

    """

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_index: int):
        table = self.restaurant.tables[table_index]
        self.view.set_controller(TableController(self.view, self.restaurant, table))


class TableController(Controller):
    """
    Table Controller

    """

    def __init__(self, view: oorms.ServerView, restaurant: Restaurant, table: Table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number: SeatNumber):
        oc = OrderController(self.view, self.restaurant, self.table, seat_number)
        self.view.set_controller(oc)

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

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item: FoodItem):
        self.order.add_item(menu_item)
        self.create_ui()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )

    def cancel(self):
        self.order.remove_unordered_items()
        self.view.set_controller(
            TableController(self.view, self.restaurant, self.table)
        )
