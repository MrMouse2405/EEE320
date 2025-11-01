"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

CustomBillController:
    Handles seat selection and custom bill creation for grouped billing.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from mvc import Controller, ViewRouter
from models import Bill, BillOrderSet, CustomBill

if TYPE_CHECKING:
    from views import CustomBillView


class CustomBillController(Controller["CustomBillView", CustomBill]):
    """
    Manages seat selection and creation of custom combined bills.
    """

    def __init__(
        self, view: "CustomBillView", model: CustomBill, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)

    def seat_touched(self, seat_number: int) -> None:
        if not self.model.table.has_order_for(seat_number):
            return

        if self.model.is_selected(seat_number):
            self.model.remove_selected_seat(seat_number)
        else:
            self.model.add_selected_seat(seat_number)

    def bill(self) -> None:
        order_sets: list[BillOrderSet] = []
        for seat in self.model.selected_seats:
            order = self.model.table.order_for(seat)
            order_sets.append(
                BillOrderSet(
                    table_location=self.model.table.location,
                    seat_number=seat,
                    items=[item.details for item in order.items],
                )
            )
            order.clear()

        _ = Bill(order_sets).save()
        self.navigation.go_back()

    def cancel(self) -> None:
        self.model.remove_all_selected_seats()
        self.navigation.go_back()
