"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

TableViewFactory:
    Factory for constructing table-specific MVC components.
"""

from tkinter import Frame
from typing import override

from controllers import TableController
from models import Table
from mvc import MVCFactory, ViewRouter
from views import TableView


class TableViewFactory(MVCFactory[TableView, Table, TableController]):
    """
    Builds and links the model, view, and controller for a single table view.
    """

    def __init__(self, navigation: ViewRouter) -> None:
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
