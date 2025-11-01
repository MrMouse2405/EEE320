"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

ServerViewFactory:
    Factory for constructing the restaurant overview MVC trio.
"""

from __future__ import annotations
from tkinter import Frame
from typing import override

from controllers import ServerController
from models import Restaurant
from mvc import MVCFactory, ViewRouter
from views import ServerView


class ServerViewFactory(MVCFactory[ServerView, Restaurant, ServerController]):
    """
    Builds and connects the model, view, and controller for the server screen.
    """

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
