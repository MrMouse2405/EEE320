import oorms
from constants import TABLES, MENU_ITEMS, NumberOfSeats, SeatNumber, TableLocation


type View = oorms.View


class Restaurant:
    def __init__(self):
        super().__init__()
        self.tables: list[Table] = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items: list[MenuItem] = [
            MenuItem(name, price) for name, price in MENU_ITEMS
        ]
        self.views: list[View] = []

    def add_view(self, view: View):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class MenuItem:
    def __init__(self, name: str, price: float):
        self.name: str = name
        self.price: float = price


class OrderItem:
    # TODO: need to represent item state, not just ordered
    def __init__(self, menu_item: MenuItem):
        self.details: MenuItem = menu_item
        self.__ordered: bool = False

    def mark_as_ordered(self):
        self.__ordered = True

    def has_been_ordered(self) -> bool:
        return self.__ordered

    def has_been_served(self) -> bool:
        # TODO: correct implementation based on item state
        return False

    def can_be_cancelled(self) -> bool:
        # TODO: correct implementation based on item state
        return True


class Order:
    def __init__(self):
        self.items: list[OrderItem] = []

    def add_item(self, menu_item: MenuItem):
        item: OrderItem = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, item: OrderItem):
        self.items.remove(item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self) -> list[OrderItem]:
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self) -> float:
        return sum((item.details.price for item in self.items))


class Table:
    def __init__(self, seats: NumberOfSeats, location: TableLocation):
        self.n_seats: NumberOfSeats = seats
        self.location: TableLocation = location
        self.orders: list[Order] = [Order() for _ in range(seats)]

    def has_any_active_orders(self) -> bool:
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat: SeatNumber) -> bool:
        return bool(self.orders[seat].items)

    def order_for(self, seat: SeatNumber) -> Order:
        return self.orders[seat]
