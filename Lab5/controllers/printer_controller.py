"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

PrinterController:
    Handles selection of printed bills and navigation to detailed bill view.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from mvc import Controller, ViewRouter
from models import BillID, Printer

if TYPE_CHECKING:
    from views import PrinterView


class PrinterController(Controller["PrinterView", Printer]):
    """
    Manages bill list interactions and transitions to bill detail views.
    """

    def __init__(
        self, view: "PrinterView", model: Printer, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)

    def on_bill_touched(self, bill_id: BillID) -> None:
        self.navigation.goto(name="bill", payload=self.model.get_bill_by_id(bill_id))
