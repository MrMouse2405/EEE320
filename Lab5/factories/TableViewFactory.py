from tkinter import Frame
from typing import override
from controllers.TableController import TableController
from models import Table
from mvc import MVCFactory, ViewRouter
from views import TableView


class TableViewFactory(MVCFactory[TableView, Table, TableController]):
    def __init__(self, model: Table, navigation: ViewRouter):
        super().__init__(navigation)
        self._model: Table = model

    @override
    def build_model(self) -> Table:
        return self._model

    @override
    def build_view(self, parent: Frame, model: Table) -> TableView:
        return TableView(parent, model)

    @override
    def build_controller(
        self, view: TableView, model: Table, navigation: ViewRouter
    ) -> TableController:
        return TableController(view, model, navigation)
