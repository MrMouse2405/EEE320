from model import Restaurant
from oorms import ServerView
from constants import Table, FoodItem, SeatNumber


class Controller:
    """
    Do not modify this class, just its subclasses. Represents common behaviour of all
    Controllers. Python has a mechanism for explicitly dealing with abstract classes,
    which we haven't seen yet; raising RuntimeError gives a similar effect.
    """

    def __init__(self, view: ServerView, restaurant: Restaurant):
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
        pass



class TableController(Controller):
    """
    Table Controller

    """

    def __init__(self, view: ServerView, restaurant: Restaurant, table: Table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def seat_touched(self, seat_number: SeatNumber):
        raise RuntimeError("seat_touched: some subclasses must implement")


class OrderController(Controller):
    """
    Order Controller

    """

    def __init__(
        self,
        view: ServerView,
        restaurant: Restaurant,
        table: Table,
        seat_number: SeatNumber,
    ):
        super().__init__(view, restaurant)
        self.table = table
        self.seat_number = seat_number

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def add_item(self, menu_tem: FoodItem):
        raise RuntimeError("add_item: some subclasses must implement")

    def update_order(self):
        raise RuntimeError("update_order: some subclasses must implement")

    def cancel(self):
        raise RuntimeError("cancel: some subclasses must implement")
