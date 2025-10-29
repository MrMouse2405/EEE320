from typing import override
from tkinter import Tk

from mvc import View
from controllers import BillController
from models import Bill


class BillView(View[BillController, Bill]):
    def __init__(self, root: Tk, model: Bill) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
