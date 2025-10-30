from __future__ import annotations
from typing import override
from collections.abc import Sequence
from mvc import ReadRepository
from models import MenuItem
from constants import MenuItemName, MENU_ITEMS


class MenuItemRepository(ReadRepository[MenuItem, MenuItemName]):
    def __init__(self) -> None:
        super().__init__()
        self.__menu_items: list[MenuItem] = [
            MenuItem(name=item[0], price=item[1]) for item in MENU_ITEMS
        ]

    @override
    def get_all(self) -> Sequence[MenuItem]:
        return self.__menu_items

    @override
    def get_by_id(self, id: MenuItemName) -> MenuItem | None:
        for item in self.__menu_items:
            if item.name == id:
                return item
        return None
