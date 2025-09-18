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
        self.tables : list[Table] = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items : list[MenuItem] = [MenuItem(name, price) for name, price in MENU_ITEMS]



class Table:
    def __init__(self, seats: NumberOfSeats, location: TableLocation):
        self.n_seat = seats
        self.location = location
        self.orders : list[Order] = [Order() for _ in range(seats)]

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
