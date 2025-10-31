"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from __future__ import annotations
from tkinter import Tk, Frame, Toplevel
from constants import SERVER_VIEW_HEIGHT, SERVER_VIEW_WIDTH
from factories import OrderViewFactory, ServerViewFactory, TableViewFactory
from mvc import ViewRouter


class App(Tk):
    def __init__(self) -> None:
        super().__init__()
        """

            Server Window

        """
        self.title("Server")
        self.server_container: Frame = Frame(
            self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        _ = self.server_container.pack_propagate(False)
        self.server_container.pack()  # or .grid(), but keep a fixed size
        self.server_router: ViewRouter = ViewRouter(
            self.server_container, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
        )
        self.server_router.register("server", ServerViewFactory(self.server_router))
        self.server_router.register("table", TableViewFactory(self.server_router))
        self.server_router.register("order", OrderViewFactory(self.server_router))
        self.server_router.goto("server")
        """

            Printer

        """
        self.printer_window: Toplevel = Toplevel(self)
        self.printer_window.title("Printer")
        self.printer_window.transient(
            self
        )  # stays on top of the main on some platforms
        self.printer_window.geometry("+120+80")  # position
        self.printer_container: Frame = Frame(
            self.printer_window,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        _ = self.printer_container.pack_propagate(False)
        self.printer_container.pack()  # or .grid(), but keep a fixed size
        self.printer_router: ViewRouter = ViewRouter(
            self.printer_container, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
        )
        self.printer_router.register("server", ServerViewFactory(self.printer_router))
        self.printer_router.goto("server")


if __name__ == "__main__":
    App().mainloop()
