from __future__ import annotations
from typing import TYPE_CHECKING
from models import Bill
from mvc import Controller, ViewRouter

if TYPE_CHECKING:
    from views import BillView


class BillController(Controller["BillView", Bill]):
    def __init__(self, view: "BillView", model: Bill, navigation: ViewRouter) -> None:
        super().__init__(view, model, navigation)

    def done(self) -> None:
        self.navigation.go_back()
