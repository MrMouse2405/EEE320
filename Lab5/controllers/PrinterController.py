from __future__ import annotations
from models import Printer
from mvc import Controller
from views import PrinterView


class PrinterController(Controller[PrinterView, Printer]):
    def __init__(self, view: PrinterView, model: Printer) -> None:
        super().__init__(view, model)

    def on_table_touch(self, table_number: int) -> None:
        print(table_number, "clicked!")
