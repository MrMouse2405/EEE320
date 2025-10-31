from __future__ import annotations
from typing import TYPE_CHECKING
from models import Bill, BillOrderSet, Table

from mvc import Controller, ViewRouter


if TYPE_CHECKING:
    from views import TableView


class TableController(Controller["TableView", Table]):
    def __init__(self, view: "TableView", model: Table, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def seat_touched(self, seat_number: int):
        print("seat touched:", seat_number)
        self.navigation.goto("order", payload=self.model.order_for(seat_number))

    def done(self):
        self.navigation.go_back()

    def bill_table(self) -> None:
        print("bill table")
        Bill(
            order_sets=[
                BillOrderSet(
                    table_location=self.model.location,
                    seat_number=seat,
                    items=[item.details for item in order.items],
                )
                for seat, order in enumerate(self.model.orders)
            ]
        ).save()
        self.model.clear_orders()
        self.navigation.go_back()

    def bill_seats(self) -> None:
        print("bill seats")
        for seat_number, order in enumerate(self.model.orders):
            bill_order_set = BillOrderSet(
                table_location=self.model.location,
                seat_number=seat_number,
                items=[item.details for item in order.items],
            )

            bill = Bill([bill_order_set])
            bill.save()
        self.model.clear_orders()
        self.navigation.go_back()

    def bill_custom(self) -> None:
        print("bill custom")
