"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from tkinter import ALL, NW, Canvas, Frame
from typing import override
from constants import (
    CANCEL_SIZE,
    CANCEL_STYLE,
    DOT_MARGIN,
    DOT_SIZE,
    GET_BUTTON_BOTTOM_LEFT,
    MENU_ITEM_SIZE,
    NOT_YET_ORDERED_STYLE,
    ORDER_ITEM_LOCATION,
    ORDERED_STYLE,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
)
from controllers import OrderController
from models import Order
from mvc import View
from views.utils import make_button


class OrderView(View[OrderController, Order]):
    def __init__(self, root: Frame, model: Order) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create order ui")
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

            make_button(self.__canvas, item.name, handler, (w, h), (x0, y0))

        self.draw_order(self.model)
        make_button(
            self.__canvas,
            "Cancel",
            lambda _: self.controller.cancel_changes(),
            location=GET_BUTTON_BOTTOM_LEFT(SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT),
        )
        make_button(
            self.__canvas, "Update Order", lambda _: self.controller.update_order()
        )

    def draw_order(self, order: Order):
        x0, h, m = ORDER_ITEM_LOCATION
        for ix, item in enumerate(order.items):
            y0 = m + ix * h
            _ = self.__canvas.create_text(x0, y0, text=item.details.name, anchor=NW)
            dot_style = (
                ORDERED_STYLE if item.has_been_placed() else NOT_YET_ORDERED_STYLE
            )
            _ = self.__canvas.create_oval(
                x0 - DOT_SIZE - DOT_MARGIN,
                y0,
                x0 - DOT_MARGIN,
                y0 + DOT_SIZE,
                **dot_style,
            )
            if item.can_be_cancelled():

                def handler(_, cancelled_item=item):
                    self.controller.remove(cancelled_item)

                make_button(
                    self.__canvas,
                    "X",
                    handler,
                    size=CANCEL_SIZE,
                    rect_style=CANCEL_STYLE,
                    location=(x0 - 2 * (DOT_SIZE + DOT_MARGIN), y0),
                )
        _ = self.__canvas.create_text(
            x0,
            m + len(order.items) * h,
            text=f"Total: {order.total_cost:.2f}",
            anchor=NW,
        )
