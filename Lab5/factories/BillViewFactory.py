from tkinter import Frame
from typing import override

from controllers.BillController import BillController
from models import Bill
from mvc import MVCFactory, ViewRouter
from repositories.BillsRepository import BillsRepository
from views import BillView

__bill_repository = BillsRepository()

class BillViewFactory(MVCFactory[BillView, Bill, BillController]):
    def __init__(self, model: Bill, navigation: ViewRouter):
        super().__init__(navigation)
        self._model: Bill = model

    @override
    def build_model(self) -> Bill:
        return self._model

    @override
    def build_view(self, parent: Frame, model: Bill) -> BillView:
        return BillView(parent, model)

    @override
    def build_controller(
        self, view: BillView, model: Bill, navigation: ViewRouter
    ) -> BillController:
        return BillController(view, model, navigation)
