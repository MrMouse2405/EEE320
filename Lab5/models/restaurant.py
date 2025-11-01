"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Restaurant:
    Central model for restaurant state.
    Stores tables and menu items used throughout the system.
"""

from collections.abc import Sequence
from mvc import Model
from constants import MENU_ITEMS, TABLES
from .menu_item import MenuItem
from .table import Table


class Restaurant(Model):
    """
    Represents the restaurant’s core model.
    Holds all tables and menu items available in the system.
    """

    def __init__(self) -> None:
        super().__init__()
        self.__tables: Sequence[Table] = [
            Table(seats, location) for seats, location in TABLES
        ]
        self.__menu_items: Sequence[MenuItem] = [
            MenuItem(name=item[0], price=item[1]) for item in MENU_ITEMS
        ]

    @property
    def tables(self) -> Sequence[Table]:
        return self.__tables

    @tables.setter
    def table(self, tables: Sequence[Table]) -> None:
        self.__tables = tables
        self.notify_views()

    @property
    def menu_items(self) -> Sequence[MenuItem]:
        return self.__menu_items

    @menu_items.setter
    def menu_items(self, menu_items: Sequence[MenuItem]) -> None:
        self.__menu_items = menu_items
        self.notify_views()
