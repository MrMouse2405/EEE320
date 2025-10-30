"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from tkinter import Canvas, Tk, Frame

from constants import SERVER_VIEW_HEIGHT, SERVER_VIEW_WIDTH
from controllers import ServerController
from factories import ServerViewFactory
from models import Restaurant
from mvc import ViewRouter
from repositories import TableRepository
from repositories.MenuItemRepository import MenuItemRepository
from views import ServerView


class App(Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("oorms lab 5")
        container = Frame(
            self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        _ = container.pack_propagate(False)
        container.pack()  # or .grid(), but keep a fixed size

        view_router: ViewRouter = ViewRouter(
            container, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
        )

        view_router.register("server", ServerViewFactory())
        view_router.goto("server")


if __name__ == "__main__":
    App().mainloop()
