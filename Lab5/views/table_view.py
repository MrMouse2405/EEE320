"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

TableView:
    Single-table view with seat selection and billing actions.
"""

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
    """
    Renders a single table with clickable seats and quick billing options.
    """

    def __init__(self, root: Frame, model: Table) -> None:
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
        self.create_table_ui()

    @override
    def refresh(self) -> None:
        self.__canvas.delete(ALL)
        self.create_table_ui()

    def create_table_ui(self) -> None:
        _, seat_ids = draw_table(
            self.__canvas, self.model, location=SINGLE_TABLE_LOCATION
        )

        for ix, seat_id in enumerate(seat_ids):

            def handler(_, seat_number=ix) -> None:
                self.controller.seat_touched(seat_number)

            _ = self.__canvas.tag_bind(seat_id, "<Button-1>", handler)

        make_button(
            canvas=self.__canvas,
            text="Done",
            action=lambda _: self.controller.done(),
        )

        if self.model.has_any_active_orders():
            button_spacing = 40
            base_x, base_y = GET_BUTTON_BOTTOM_LEFT(
                SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
            )

            actions = [
                ("Custom Bill", self.controller.bill_custom),
                ("Bill Table", self.controller.bill_table),
                ("Bill Seats", self.controller.bill_seats),
            ]

            for i, (label, func) in enumerate(actions):
                make_button(
                    canvas=self.__canvas,
                    text=label,
                    action=lambda _evt, f=func: f(),
                    location=(base_x, base_y - i * button_spacing),
                )
