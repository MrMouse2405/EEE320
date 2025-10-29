from typing import override
from tkinter import Tk
from controllers import TableController
from mvc import View
from models import Table


class TableView(View[TableController, Table]):
    def __init__(self, root: Tk, model: Table) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
