"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

ServerController:
    Handles user interactions on the restaurant floor layout
    and routes to specific table views.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from mvc import Controller, ViewRouter
from models import Restaurant

if TYPE_CHECKING:
    from views import ServerView


class ServerController(Controller["ServerView", Restaurant]):
    """
    Manages events and navigation from the restaurant overview screen.
    """

    def __init__(
        self, view: "ServerView", model: Restaurant, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)
        view.create_restaurant_ui()

    def on_table_touch(self, table_number: int) -> None:
        self.navigation.goto("table", payload=self.model.tables[table_number])
