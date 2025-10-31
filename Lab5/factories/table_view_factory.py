from tkinter import Frame
from typing import override
from controllers import TableController
from models import Table
from mvc import MVCFactory, ViewRouter
from views import TableView


class TableViewFactory(MVCFactory[TableView, Table, TableController]):
    def __init__(self, navigation: ViewRouter):
        super().__init__(navigation)

    @override
    def build_model(self) -> Table:
        raise Exception("Requires Table Payload!")

    @override
    def build_view(self, parent: Frame, model: Table) -> TableView:
        return TableView(parent, model)

    @override
    def build_controller(
        self, view: TableView, model: Table, navigation: ViewRouter
    ) -> TableController:
        return TableController(view, model, navigation)
