"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

CustomBillViewFactory:
    Factory for constructing MVC components used in custom bill creation.
"""

from tkinter import Frame
from typing import override

from controllers import CustomBillController
from models import CustomBill
from mvc import MVCFactory, ViewRouter
from views import CustomBillView


class CustomBillViewFactory(
    MVCFactory[CustomBillView, CustomBill, CustomBillController]
):
    """
    Builds and links the model, view, and controller for the custom bill view.
    """

    def __init__(self, navigation: ViewRouter) -> None:
        super().__init__(navigation)

    @override
    def build_model(self) -> CustomBill:
        raise Exception("Requires Table Payload!")

    @override
    def build_view(self, parent: Frame, model: CustomBill) -> CustomBillView:
        return CustomBillView(parent, model)

    @override
    def build_controller(
        self, view: CustomBillView, model: CustomBill, navigation: ViewRouter
    ) -> CustomBillController:
        return CustomBillController(view, model, navigation)
