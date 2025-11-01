"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

ServerView:
    Top-level floor view showing all tables with clickable hit targets.
"""

from tkinter import ALL, Canvas, Frame
from typing import override
from collections.abc import Sequence

from constants import RESTAURANT_SCALE, SERVER_VIEW_HEIGHT, SERVER_VIEW_WIDTH
from controllers import ServerController
from models import Table
from models.restaurant import Restaurant
from mvc import View
from views.utils import draw_table


class ServerView(View[ServerController, Restaurant]):
    """
    Renders the restaurant layout and forwards table/seat clicks to the controller.
    """

    def __init__(self, root: Frame, model: Restaurant) -> None:
        super().__init__(root, model)
        self.__Frame: Frame = root  # kept as-is if referenced elsewhere
        self.__animating: bool = False
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
            # Capture current ix for the handler
            def table_touch_handler(_, table_number: int = ix) -> None:
                _ = self.controller.on_table_touch(table_number)

            _ = self.__canvas.tag_bind(table_id, "<Button-1>", table_touch_handler)
            for seat_id in seat_ids:
                _ = self.__canvas.tag_bind(seat_id, "<Button-1>", table_touch_handler)
