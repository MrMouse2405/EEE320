from __future__ import annotations
from collections.abc import Generator, Sequence
from typing import Literal
from mvc import Model
from .OrderItem import OrderItem
from .MenuItem import MenuItem


class Order(Model):
    def __init__(self) -> None:
        super().__init__()
        self.__items: list[OrderItem] = []

    @property
    def items(self) -> Sequence[OrderItem]:
        return self.__items

    @property
    def requested_items(self) -> Generator[OrderItem, None, None]:
        return (item for item in self.__items if not item.has_been_placed())

    @property
    def total_cost(self) -> float | Literal["0"]:
        return sum((item.details.price for item in self.__items))

    def add_item(self, menu_item: MenuItem) -> None:
        self.__items.append(OrderItem(menu_item))
        self.notify_views()

    def remove_item(self, order_item: OrderItem) -> None:
        self.__items.remove(order_item)
        self.notify_views()

    def place_new_orders(self) -> None:
        for item in self.requested_items:
            item.mark_as_placed()
        self.notify_views()

    def remove_requested_item(self) -> None:
        for item in self.requested_items:
            self.__items.remove(item)
        self.notify_views()
