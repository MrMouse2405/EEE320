"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

TableController:
    Handles seat interactions and billing operations for a single table.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from mvc import Controller, ViewRouter
from models import Bill, BillOrderSet, CustomBill, Table

if TYPE_CHECKING:
    from views import TableView


class TableController(Controller["TableView", Table]):
    """
    Manages seat selection, billing actions, and navigation for table interactions.
    """

    def __init__(self, view: "TableView", model: Table, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def seat_touched(self, seat_number: int) -> None:
        self.navigation.goto("order", payload=self.model.order_for(seat_number))

    def done(self) -> None:
        self.navigation.go_back()

    def bill_table(self) -> None:
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
        for seat_number, order in enumerate(self.model.orders):
            if order.items:
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
        self.navigation.goto(name="custom_bill", payload=CustomBill(self.model))
