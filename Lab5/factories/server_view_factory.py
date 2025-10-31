from __future__ import annotations
from tkinter import Frame
from typing import override
from controllers import ServerController
from models import Restaurant
from mvc import MVCFactory, ViewRouter
from views import ServerView


class ServerViewFactory(MVCFactory[ServerView, Restaurant, ServerController]):
    @override
    def build_model(self) -> Restaurant:
        return Restaurant()

    @override
    def build_view(self, parent: Frame, model: Restaurant) -> ServerView:
        return ServerView(parent, model)

    @override
    def build_controller(
        self, view: ServerView, model: Restaurant, navigation: ViewRouter
    ) -> ServerController:
        return ServerController(view, model, navigation)
