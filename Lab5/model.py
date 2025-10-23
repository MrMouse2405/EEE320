"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from __future__ import annotations
from enum import Enum, auto
from constants import TABLES, MENU_ITEMS
import oorms

type RestaurantView = oorms.RestaurantView


class Restaurant:
    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view: RestaurantView):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:
    def __init__(self, seats: int, location: int):
        self.n_seats: int = seats
        self.location: int = location
        self.orders: list[Order] = [Order() for _ in range(seats)]

    def has_any_active_orders(self) -> bool:
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat: int) -> bool:
        return bool(self.orders[seat].items)

    def order_for(self, seat: int) -> Order:
        return self.orders[seat]


class Order:
    def __init__(self):
        self.items: list[OrderItem] = []

    def add_item(self, menu_item: MenuItem):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item: OrderItem):
        self.items.remove(order_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self) -> list[OrderItem]:
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self) -> int:
        return sum((item.details.price for item in self.items))


class OrderState(Enum):
    REQUESTED = auto()
    PLACED = auto()
    COOKING = auto()
    READY = auto()
    SERVED = auto()
    CANCELLED = auto()


class OrderItem:
    def __init__(self, menu_item: MenuItem):
        self.details: MenuItem = menu_item
        self.__state: OrderState = OrderState.REQUESTED

    def mark_as_ordered(self):
        self.__state = OrderState.PLACED

    def has_been_ordered(self) -> bool:
        return self.__state != OrderState.REQUESTED

    def mark_as_served(self):
        self.__state = OrderState.SERVED

    def has_been_served(self) -> bool:
        return self.__state == OrderState.SERVED

    def can_be_cancelled(self) -> bool:
        return self.__state == OrderState.REQUESTED or self.__state == OrderState.PLACED

    def get_order_state(self) -> OrderState:
        return self.__state

    def mark_as_cooking(self):
        self.__state = OrderState.COOKING

    def has_been_cooking(self) -> bool:
        return self.__state == OrderState.COOKING

    def mark_as_ready(self):
        self.__state = OrderState.READY

    def has_been_ready(self) -> bool:
        return self.__state == OrderState.READY

    def has_been_cancelled(self) -> bool:
        return self.__state == OrderState.CANCELLED

    def mark_as_cancelled(self):
        self.__state = OrderState.CANCELLED


class MenuItem:
    def __init__(self, name: str, price: float):
        self.name: str = name
        self.price: float = price
