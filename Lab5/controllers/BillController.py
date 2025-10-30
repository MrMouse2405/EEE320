from __future__ import annotations
from models import Bill
from mvc import Controller, ViewRouter
from views import BillView


class BillController(Controller[BillView, Bill]):
    def __init__(self, view: BillView, model: Bill, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

