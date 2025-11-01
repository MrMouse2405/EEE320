"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

App:
    Entry point of the program. Initializes the main server and printer windows
    and configures their respective MVC navigation routes.
"""

from __future__ import annotations
from tkinter import Tk, Frame, Toplevel
from constants import (
    PRINTER_VIEW_HEIGHT,
    PRINTER_VIEW_WIDTH,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
)
from factories import (
    BillViewFactory,
    CustomBillViewFactory,
    OrderViewFactory,
    ServerViewFactory,
    TableViewFactory,
    PrinterViewFactory,
)
from mvc import ViewRouter


class App(Tk):
    """
    Main application window that initializes both the server and printer interfaces.
    """

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
        self.server_container.pack()
        self.server_router: ViewRouter = ViewRouter(
            self.server_container, SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
        )
        self.server_router.register("server", ServerViewFactory(self.server_router))
        self.server_router.register("table", TableViewFactory(self.server_router))
        self.server_router.register("order", OrderViewFactory(self.server_router))
        self.server_router.register(
            "custom_bill", CustomBillViewFactory(self.server_router)
        )
        self.server_router.goto("server")

        """
        Printer Window
        """
        self.printer_window: Toplevel = Toplevel(self)
        self.printer_window.title("Printer")
        self.printer_window.transient(self)
        self.printer_window.geometry("+120+80")
        self.printer_container: Frame = Frame(
            self.printer_window,
            width=PRINTER_VIEW_WIDTH,
            height=PRINTER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        _ = self.printer_container.pack_propagate(False)
        self.printer_container.pack()
        self.printer_router: ViewRouter = ViewRouter(
            self.printer_container, PRINTER_VIEW_WIDTH, PRINTER_VIEW_HEIGHT
        )
        self.printer_router.register("printer", PrinterViewFactory(self.printer_router))
        self.printer_router.register("bill", BillViewFactory(self.printer_router))
        self.printer_router.goto("printer")


if __name__ == "__main__":
    App().mainloop()
