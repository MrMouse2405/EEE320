from __future__ import annotations
from factories.OrderViewFactory import OrderViewFactory
from models import Table
from mvc import Controller, ViewRouter
from views import TableView


class TableController(Controller[TableView, Table]):
    def __init__(self, view: TableView, model: Table, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def seat_touched(self, seat_number: int):
        print("seat touched:", seat_number)
        self.navigation.register(
            "order",
            OrderViewFactory(self.model.order_for(seat_number), self.navigation),
        )
        self.navigation.goto("order")

    def done(self):
        self.navigation.go_back()

    def make_bills(self):
        print("make bills")
