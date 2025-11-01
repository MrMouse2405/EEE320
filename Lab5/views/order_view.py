"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

OrderView:
    Menu-driven order screen with per-item status and cancel/update actions.
"""

from typing import override
from tkinter import ALL, NW, Canvas, Frame

from constants import (
    CANCEL_SIZE,
    CANCEL_STYLE,
    CANCEL_STYLE_FILL,
    CANCEL_STYLE_OUTLINE,
    DOT_MARGIN,
    DOT_SIZE,
    GET_BUTTON_BOTTOM_LEFT,
    MENU_ITEM_SIZE,
    NOT_YET_ORDERED_STYLE_FILL,
    NOT_YET_ORDERED_STYLE_OUTLINE,
    ORDER_ITEM_LOCATION,
    ORDERED_STYLE_FILL,
    ORDERED_STYLE_OUTLINE,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
)
from controllers import OrderController
from models import Order
from mvc import View
from views.utils import make_button


class OrderView(View[OrderController, Order]):
    """
    Renders menu buttons and the current order list with item state and actions.
    """

    def __init__(self, root: Frame, model: Order) -> None:
        super().__init__(root, model)
        self.__canvas: Canvas

    @override
    def create_ui(self) -> None:
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

    def create_order_ui(self) -> None:
        for ix, item in enumerate(self.model.menu_items):
            w, h, margin = MENU_ITEM_SIZE
            x0 = margin
            y0 = margin + (h + margin) * ix

            def handler(_, menuitem=item) -> None:
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
            self.__canvas,
            "Update Order",
            lambda _: self.controller.update_order(),
        )

    def draw_order(self, order: Order) -> None:
        x0, h, m = ORDER_ITEM_LOCATION
        for ix, item in enumerate(order.items):
            y0 = m + ix * h
            _ = self.__canvas.create_text(x0, y0, text=item.details.name, anchor=NW)

            if item.has_been_placed():
                _ = self.__canvas.create_oval(
                    x0 - DOT_SIZE - DOT_MARGIN,
                    y0,
                    x0 - DOT_MARGIN,
                    y0 + DOT_SIZE,
                    fill=ORDERED_STYLE_FILL,
                    outline=ORDERED_STYLE_OUTLINE,
                )
            else:
                _ = self.__canvas.create_oval(
                    x0 - DOT_SIZE - DOT_MARGIN,
                    y0,
                    x0 - DOT_MARGIN,
                    y0 + DOT_SIZE,
                    fill=NOT_YET_ORDERED_STYLE_FILL,
                    outline=NOT_YET_ORDERED_STYLE_OUTLINE,
                )

            if item.can_be_cancelled():

                def handler(_, cancelled_item=item) -> None:
                    self.controller.remove(cancelled_item)

                make_button(
                    self.__canvas,
                    "X",
                    handler,
                    size=CANCEL_SIZE,
                    fill=CANCEL_STYLE_FILL,
                    outline=CANCEL_STYLE_OUTLINE,
                    location=(x0 - 2 * (DOT_SIZE + DOT_MARGIN), y0),
                )

        _ = self.__canvas.create_text(
            x0,
            m + len(order.items) * h,
            text=f"Total: {order.total_cost:.2f}",
            anchor=NW,
        )
