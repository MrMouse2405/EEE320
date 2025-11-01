from __future__ import annotations
from tkinter import Frame
from typing import override
from controllers import PrinterController
from models import Printer
from mvc import MVCFactory, ViewRouter
from views import PrinterView


class PrinterViewFactory(MVCFactory[PrinterView, Printer, PrinterController]):
    @override
    def build_model(self) -> Printer:
        return Printer()

    @override
    def build_view(self, parent: Frame, model: Printer) -> PrinterView:
        return PrinterView(parent, model)

    @override
    def build_controller(
        self, view: PrinterView, model: Printer, navigation: ViewRouter
    ) -> PrinterController:
        return PrinterController(view, model, navigation)
