from __future__ import annotations
from models import Restaurant
from mvc import Controller
from views import ServerView


class ServerController(Controller[ServerView, Restaurant]):
    def __init__(self, view: ServerView, model: Restaurant) -> None:
        super().__init__(view, model)
        view.create_restaurant_ui()

    def on_table_touch(self, table_number: int) -> None:
        self.view.refresh()
        print(table_number, "clicked!")
