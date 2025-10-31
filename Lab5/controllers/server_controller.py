from __future__ import annotations
from models import Restaurant
from mvc import Controller, ViewRouter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from views import ServerView


class ServerController(Controller["ServerView", Restaurant]):
    def __init__(
        self, view: "ServerView", model: Restaurant, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)
        view.create_restaurant_ui()

    def on_table_touch(self, table_number: int) -> None:
        self.navigation.goto("table", payload=self.model.tables[table_number])
