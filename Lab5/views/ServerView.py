"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez
"""

from tkinter import ALL, Frame, Tk, Canvas
from typing import override, Callable
from collections.abc import Sequence
from controllers import ServerController
from models.Restaurant import Restaurant
from mvc import View
from models import Table
from constants import (
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
    RESTAURANT_SCALE,
)
from views.utils import draw_table


class ServerView(View[ServerController, Restaurant]):
    def __init__(self, root: Frame, model: Restaurant) -> None:
        super().__init__(root, model)
        self.__Frame: Frame = root
        self.__animating: bool = False

    @override
    def create_ui(self) -> None:
        print("create ui")
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
        self.create_restaurant_ui()

    @override
    def refresh(self) -> None:
        self.__canvas.delete(ALL)
        self.create_restaurant_ui()

    def create_restaurant_ui(self, tag: str = "scene") -> None:
        tables: Sequence[Table] = self.model.tables
        view_ids: list[tuple[int, list[int]]] = []

        for ix, table in enumerate(tables):
            table_id, seat_ids = draw_table(
                self.__canvas, table, scale=RESTAURANT_SCALE
            )
            view_ids.append((table_id, seat_ids))
            # Tag everything that belongs to the scene
            self.__canvas.addtag_withtag(tag, table_id)
            for sid in seat_ids:
                self.__canvas.addtag_withtag(tag, sid)

        for ix, (table_id, seat_ids) in enumerate(view_ids):
            # §54.7 "extra arguments trick" in Tkinter 8.5 reference by Shipman
            # Used to capture current value of ix as table_index for use when
            # handler is called (i.e., when screen is clicked).
            def table_touch_handler(_, table_number: int = ix):
                _ = self.controller.on_table_touch(table_number)

            _ = self.__canvas.tag_bind(table_id, "<Button-1>", table_touch_handler)
            for seat_id in seat_ids:
                _ = self.__canvas.tag_bind(seat_id, "<Button-1>", table_touch_handler)
