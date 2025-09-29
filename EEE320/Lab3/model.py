from constants import TABLES, MENU_ITEMS, SeatNumber, NumberOfSeats, TableLocation, Cost


class Restaurant:
    def __init__(self):
        self.tables: list[Table] = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items: list[MenuItem] = [
            MenuItem(name, price) for name, price in MENU_ITEMS
        ]


class MenuItem:
    def __init__(self, name: str, price: float):
        self.name: str = name
        self.price: float = price


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
        return [item for item in self.items if not item.ordered]

    def place_new_orders(self):
        for item in self.items:
            item.mark_as_ordered()

    def remove_unordered_items(self):
        self.items = [item for item in self.items if item.ordered]

    def total_cost(self) -> Cost:
        return sum(item.details.price for item in self.items)


class Table:
    def __init__(self, seats: NumberOfSeats, location: TableLocation):
        self.n_seats: NumberOfSeats = seats
        self.location: TableLocation = location
        self.orders: list[Order] = [Order() for _ in range(seats)]

    def has_order_for(self, seat: SeatNumber) -> bool:
        return len(self.orders[seat].items) != 0

    def order_for(self, seat: SeatNumber) -> Order:
        return self.orders[seat]
