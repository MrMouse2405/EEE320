from __future__ import annotations
from typing import TYPE_CHECKING
from uuid import UUID
from models import Printer
from mvc import Controller, ViewRouter

if TYPE_CHECKING:
    from views import PrinterView


class PrinterController(Controller["PrinterView", Printer]):
    def __init__(
        self, view: "PrinterView", model: Printer, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)

    def on_bill_touched(self, bill_id: UUID) -> None:
        self.navigation.goto(name="bill", payload=self.model.get_bill_by_id(bill_id))
