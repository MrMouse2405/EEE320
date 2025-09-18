class Controller:
    """
    Do not modify this class, just its subclasses. Represents common behaviour of all
    Controllers. Python has a mechanism for explicitly dealing with abstract classes,
    which we haven't seen yet; raising RuntimeError gives a similar effect.
    """

    def __init__(self, view, restaurant):
        self.view = view
        self.restaurant = restaurant

    def add_item(self, item):
        raise RuntimeError("add_item: some subclasses must implement")

    def cancel(self):
        raise RuntimeError("cancel: some subclasses must implement")

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def done(self):
        raise RuntimeError("done: some subclasses must implement")

    def place_order(self):
        raise RuntimeError("place_order: some subclasses must implement")

    def seat_touched(self, seat_number):
        raise RuntimeError("seat_touched: some subclasses must implement")

    def table_touched(self, table_index):
        raise RuntimeError("table_touched: some subclasses must implement")


class RestaurantController(Controller):
    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_index):
        raise RuntimeError("table_touched: some subclasses must implement")

class TableController(Controller):
    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def seat_touched(self, seat_number):
        raise RuntimeError("seat_touched: some subclasses must implement")


class OrderController(Controller):
    def __init__(self, view, restaurant, table, seat_number):
        super().__init__(view, restaurant)
        self.table = table
        self.seat_number = seat_number

    def create_ui(self):
        raise RuntimeError("create_ui: all subclasses must implement")

    def add_item(self, menu_tem):
        raise RuntimeError("add_item: some subclasses must implement")

    def update_order(self):
        raise RuntimeError("update_order: some subclasses must implement")

    def cancel(self):
        raise RuntimeError("cancel: some subclasses must implement")
