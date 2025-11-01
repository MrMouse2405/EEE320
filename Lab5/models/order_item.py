"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

OrderItem:
    Represents individual menu items within an order.
    Tracks the item’s state (requested, placed, or billed).
"""

from enum import Enum, auto
from mvc import Model
from .menu_item import MenuItem


class OrderState(Enum):
    """Defines possible states for an order item."""

    REQUESTED = auto()
    PLACED = auto()
    BILLED = auto()


class OrderItem(Model):
    """
    Represents a single menu item in an order.
    Manages its state and provides status transitions.
    """

    def __init__(self, menu_item: MenuItem) -> None:
        super().__init__()
        self.__details: MenuItem = menu_item
        self.__state: OrderState = OrderState.REQUESTED

    @property
    def details(self) -> MenuItem:
        return self.__details

    @property
    def state(self) -> OrderState:
        return self.__state

    @state.setter
    def state(self, state: OrderState) -> None:
        self.__state = state
        self.notify_views()

    def has_been_placed(self) -> bool:
        return self.__state == OrderState.PLACED

    def has_been_billed(self) -> bool:
        return self.__state == OrderState.BILLED

    def mark_as_placed(self) -> None:
        self.state = OrderState.PLACED

    def mark_as_billed(self) -> None:
        self.state = OrderState.BILLED

    def can_be_cancelled(self) -> bool:
        return not self.has_been_billed()
