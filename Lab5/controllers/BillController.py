from __future__ import annotations
from models import Bill
from mvc import Controller
from views import BillView


class BillController(Controller[BillView, Bill]):
    def __init__(self, view: BillView, model: Bill) -> None:
        super().__init__(view, model)
