from __future__ import annotations
from typing import TYPE_CHECKING
from models import Printer
from mvc import Controller, ViewRouter

if TYPE_CHECKING:
    from views import PrinterView


class PrinterController(Controller["PrinterView", Printer]):
    def __init__(
        self, view: "PrinterView", model: Printer, navigation: ViewRouter
    ) -> None:
        super().__init__(view, model, navigation)

    def on_table_touch(self, table_number: int) -> None:
        print(table_number, "clicked!")
