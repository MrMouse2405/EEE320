from __future__ import annotations
from models import Table
from mvc import Controller, ViewRouter
from views import TableView


class TableController(Controller[TableView, Table]):
    def __init__(self, view: TableView, model: Table, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def seat_touched(self, seat_number: int):
        print("seat touched:", seat_number)

    def done(self):
        self.navigation.go_back()

    def make_bills(self):
        print("make bills")
