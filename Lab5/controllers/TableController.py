from __future__ import annotations
from models import Table
from mvc import Controller
from views import TableView


class TableController(Controller[TableView, Table]):
    def __init__(self, view: TableView, model: Table) -> None:
        super().__init__(view, model)
