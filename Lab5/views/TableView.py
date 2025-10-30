"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from typing import override
from tkinter import Frame
from controllers import TableController
from mvc import View
from models import Table


class TableView(View[TableController, Table]):
    def __init__(self, root: Frame, model: Table) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
