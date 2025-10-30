"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from typing import override
from tkinter import Frame

from mvc import View
from controllers import BillController
from models import Bill


class BillView(View[BillController, Bill]):
    def __init__(self, root: Frame, model: Bill) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
