from constants import (
    TABLES,
    MENU_ITEMS,
    SeatNumber,
    FoodItem,
    NumberOfSeats,
    TableLocation,
    Cost
)


class Restaurant:
    def __init__(self):
        self.tables: list[Table] = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items: list[MenuItem] = [MenuItem(name, price) for name, price in MENU_ITEMS]


class MenuItem:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class OrderItem:
    def __init__(self, menu_item: MenuItem):
        self.details: MenuItem = menu_item
        self.ordered: bool = False

    def mark_as_ordered(self):
        self.ordered = True


class Order:
    def __init__(self):
        self.items: list[OrderItem] = []

    def add_item(self, menu_item: MenuItem):
        self.items.append(OrderItem(menu_item))

    def unordered_items(self) -> list[OrderItem]:
        unordered_items = []
        for item in self.items:
            if not item.ordered:
                unordered_items.append(item)
        return unordered_items

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.items:
            if not item.ordered:
                self.items.remove(item)

    def total_cost(self) -> Cost:
        total_cost = 0
        for item in self.items:
            total_cost += item.price
        return total_cost


class Table:
    def __init__(self, seats: NumberOfSeats, location: TableLocation):
        self.n_seat = seats
        self.location = location
        self.orders: list[Order] = [Order() for _ in range(seats)]

    def has_order_for(self, seat: SeatNumber):
        pass

    def order_for(self, seat: SeatNumber) -> Order:
        return self.orders[seat]
