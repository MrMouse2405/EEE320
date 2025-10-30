"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from tkinter import ALL, Canvas, Frame
from typing import override
from constants import (
    GET_BUTTON_BOTTOM_LEFT,
    MENU_ITEM_SIZE,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
)
from controllers import OrderController
from models import Order
from mvc import View


class OrderView(View[OrderController, Order]):
    def __init__(self, root: Frame, model: Order) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create order ui")
        self.grid()
        self.__canvas = Canvas(
            master=self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.__canvas.grid()
        self.__canvas.update()

    @override
    def refresh(self) -> None:
        self.__canvas.delete(ALL)
        self.create_order_ui()

    def create_order_ui(self):
        for ix, item in enumerate(self.model.menu_items):
            w, h, margin = MENU_ITEM_SIZE
            x0 = margin
            y0 = margin + (h + margin) * ix

            def handler(_, menuitem=item):
                self.controller.add_item(menuitem)

            self.make_button(item.name, handler, (w, h), (x0, y0))
        draw_order(self.__canvas, self.model)
        self.make_button(
            self.__canvas,
            "Cancel",
            lambda event: self.controller.cancel_changes(),
            location=GET_BUTTON_BOTTOM_LEFT(SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT),
        )
        self.make_button("Update Order", lambda event: self.controller.update_order())
