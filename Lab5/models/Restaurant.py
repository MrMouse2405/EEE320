from collections.abc import Sequence
from models import MenuItem, Table
from mvc import Model


class Restaurant(Model):
    def __init__(self, tables: Sequence[Table], menu_items: Sequence[MenuItem]) -> None:
        super().__init__()
        self.__tables: Sequence[Table] = tables
        self.__menu_items: Sequence[MenuItem] = menu_items

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
