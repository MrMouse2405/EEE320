"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

BillViewFactory:
    Factory for constructing MVC components for displaying a single bill.
"""

from tkinter import Frame
from typing import override

from controllers import BillController
from models import Bill
from mvc import MVCFactory, ViewRouter
from views import BillView


class BillViewFactory(MVCFactory[BillView, Bill, BillController]):
    """
    Builds and links the model, view, and controller for a bill view.
    """

    def __init__(self, navigation: ViewRouter) -> None:
        super().__init__(navigation)

    @override
    def build_model(self) -> Bill:
        raise Exception("Requires Bill Payload!")

    @override
    def build_view(self, parent: Frame, model: Bill) -> BillView:
        return BillView(parent, model)

    @override
    def build_controller(
        self, view: BillView, model: Bill, navigation: ViewRouter
    ) -> BillController:
        return BillController(view, model, navigation)
