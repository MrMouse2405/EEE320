import math
from tkinter import ALL, Tk, Canvas
from typing import override, Callable
from collections.abc import Sequence
from controllers import ServerController
from models.Restaurant import Restaurant
from mvc import View
from models import Table
from constants import (
    EMPTY_SEAT_FILL,
    FULL_SEAT_FILL,
    FULL_SEAT_OUTLINE,
    GET_BUTTON_BOTTOM_RIGHT,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
    SEAT_DIAM,
    SEAT_SPACING,
    TABLE_FILL,
    TABLE_OUTLINE,
    TABLE_WIDTH,
    SINGLE_TABLE_LOCATION,
    BUTTON_SIZE,
    BUTTON_STYLE,
    BUTTON_TEXT_STYLE,
    ORDER_ITEM_LOCATION,
    DOT_SIZE,
    DOT_MARGIN,
    NOT_YET_ORDERED_STYLE,
    ORDERED_STYLE,
    RESTAURANT_SCALE,
    MENU_ITEM_SIZE,
    CANCEL_SIZE,
    CANCEL_STYLE,
    TableLocation,
)
from views.utils import draw_table


class ServerView(View[ServerController, Restaurant]):
    def __init__(self, root: Tk, model: Restaurant) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")
        self.grid()
        self.__canvas: Canvas = Canvas(
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
        self.create_restaurant_ui()

    def create_restaurant_ui(self) -> None:
        tables: Sequence[Table] = self.model.tables
        view_ids: list[tuple[int, list[int]]] = []

        for ix, table in enumerate(tables):
            table_id, seat_ids = draw_table(
                self.__canvas, table, scale=RESTAURANT_SCALE
            )
            view_ids.append((table_id, seat_ids))

        for ix, (table_id, seat_ids) in enumerate(view_ids):
            # §54.7 "extra arguments trick" in Tkinter 8.5 reference by Shipman
            # Used to capture current value of ix as table_index for use when
            # handler is called (i.e., when screen is clicked).
            def table_touch_handler(_, table_number: int = ix):
                _ = self.controller.on_table_touch(table_number)

            _ = self.__canvas.tag_bind(table_id, "<Button-1>", table_touch_handler)
            for seat_id in seat_ids:
                _ = self.__canvas.tag_bind(seat_id, "<Button-1>", table_touch_handler)
