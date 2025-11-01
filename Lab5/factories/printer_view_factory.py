"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

PrinterViewFactory:
    Factory for constructing the printer MVC components.
"""

from __future__ import annotations
from tkinter import Frame
from typing import override

from controllers import PrinterController
from models import Printer
from mvc import MVCFactory, ViewRouter
from views import PrinterView


class PrinterViewFactory(MVCFactory[PrinterView, Printer, PrinterController]):
    """
    Builds and connects the model, view, and controller for the printer view.
    """

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
