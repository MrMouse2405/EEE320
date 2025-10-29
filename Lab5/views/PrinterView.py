from typing import override
from tkinter import Tk
from models import Printer
from controllers import PrinterController
from mvc import View


class PrinterView(View[PrinterController, Printer]):
    def __init__(self, root: Tk, model: Printer) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
