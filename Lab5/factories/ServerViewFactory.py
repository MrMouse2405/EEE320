from __future__ import annotations
from tkinter import Frame
from typing import override
from controllers import ServerController
from models import Restaurant
from mvc import MVCFactory, ViewRouter
from repositories import MenuItemRepository, TableRepository
from views import ServerView

_table_repository = TableRepository()
_menu_item_repository = MenuItemRepository()


class ServerViewFactory(MVCFactory[ServerView, Restaurant, ServerController]):
    @override
    def build_model(self) -> Restaurant:
        return Restaurant(_table_repository.get_all(), _menu_item_repository.get_all())

    @override
    def build_view(self, parent: Frame, model: Restaurant) -> ServerView:
        return ServerView(parent, model)

    @override
    def build_controller(
        self, view: ServerView, model: Restaurant, navigation: ViewRouter
    ) -> ServerController:
        return ServerController(view, model, navigation)
