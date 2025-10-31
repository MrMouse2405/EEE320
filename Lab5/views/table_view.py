"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from functools import partial
from typing import override
from tkinter import ALL, Canvas, Frame
from constants import (
    GET_BUTTON_BOTTOM_LEFT,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
    SINGLE_TABLE_LOCATION,
)
from controllers import TableController
from mvc import View
from models import Table
from views.utils import draw_table, make_button


class TableView(View[TableController, Table]):
    def __init__(self, root: Frame, model: Table) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create table ui")
        self.__canvas = Canvas(
            master=self,
            width=SERVER_VIEW_WIDTH,
            height=SERVER_VIEW_HEIGHT,
            borderwidth=0,
            highlightthickness=0,
        )
        self.__canvas.grid()
        self.__canvas.update()
        self.create_table_ui(self.model)

    @override
    def refresh(self) -> None:
        print("refresh table ui")
        self.__canvas.delete(ALL)
        self.create_table_ui(self.model)

    def create_table_ui(self, table: Table):
        table_id, seat_ids = draw_table(
            self.__canvas, table, location=SINGLE_TABLE_LOCATION
        )
        for ix, seat_id in enumerate(seat_ids):

            def handler(_, seat_number=ix):
                self.controller.seat_touched(seat_number)

            _ = self.__canvas.tag_bind(seat_id, "<Button-1>", handler)

        make_button(
            canvas=self.__canvas,
            text="Done",
            action=lambda _: self.controller.done(),
        )

        if table.has_any_active_orders():
            BUTTON_SPACING = 40

            base_x, base_y = GET_BUTTON_BOTTOM_LEFT(
                SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
            )

            for i, (label, handler) in enumerate(
                [
                    ("Custom Bill", self.controller.bill_custom),
                    ("Bill Table", self.controller.bill_table),
                    ("Bill Seats", self.controller.bill_seats),
                ]
            ):
                make_button(
                    canvas=self.__canvas,
                    text=label,
                    action=partial(lambda f, _evt=None: f(), handler),
                    location=(base_x, base_y - i * BUTTON_SPACING),
                )
