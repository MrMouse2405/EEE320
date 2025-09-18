from constants import (
    TABLES,
    MENU_ITEMS,
    SeatNumber,
    MenuItem,
    NumberOfSeats,
    TableLocation,
)


class Restaurant:
    def __init__(self):
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        # TODO: uncomment next line
        # self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]


class Table:
    def __init__(self, seats: NumberOfSeats, location: TableLocation):
        self.n_seats = seats
        self.location = location
        # TODO: Uncomment next line
        # self.orders = [Order() for _ in range(seats)]

    def has_order_for(self, seat: SeatNumber):
        pass

    def order_for(self, seat: SeatNumber):
        pass


class Order:
    def __init__(self):
        pass

    def add_item(self, menu_item: MenuItem):
        pass

    def unordered_items(self):
        pass

    def place_order(self):
        pass

    def remove_unordered_items(self):
        pass

    def total_cost(self):
        pass


class OrderItem:
    def __init__(self, menu_item: MenuItem):
        self.menu_item = menu_item

    def mark_as_ordered(self):
        pass


class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price
