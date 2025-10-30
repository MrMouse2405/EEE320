from __future__ import annotations
from factories.TableViewFactory import TableViewFactory
from models import Restaurant
from mvc import Controller, ViewRouter
from views import ServerView


class ServerController(Controller[ServerView, Restaurant]):
    def __init__(
        self, view: ServerView, model: Restaurant, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)
        view.create_restaurant_ui()

    def on_table_touch(self, table_number: int) -> None:
        print(TableViewFactory)
        self.navigation.register(
            "table",
            TableViewFactory(self.model.tables[table_number], self.navigation),
        )
        self.navigation.goto("table")
