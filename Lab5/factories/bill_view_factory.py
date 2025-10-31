from tkinter import Frame
from typing import override

from controllers import BillController
from models import Bill
from mvc import MVCFactory, ViewRouter
from views import BillView


class BillViewFactory(MVCFactory[BillView, Bill, BillController]):
    def __init__(self, navigation: ViewRouter):
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
