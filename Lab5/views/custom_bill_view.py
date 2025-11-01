"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

CustomBillView:
    Seat-selection view for creating a combined bill from multiple seats.
"""

from __future__ import annotations

import math
from typing import override
from tkinter import ALL, Canvas, Frame

from constants import (
    EMPTY_SEAT_FILL,
    EMPTY_SEAT_OUTLINE,
    FULL_SEAT_FILL,
    FULL_SEAT_OUTLINE,
    GET_BUTTON_BOTTOM_LEFT,
    SEAT_DIAM,
    SEAT_SPACING,
    SELECTED_SEAT_FILL,
    SELECTED_SEAT_OUTLINE,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
    SINGLE_TABLE_LOCATION,
    TABLE_OUTLINE,
    TABLE_WIDTH,
    NumberOfSeats,
)
from controllers import CustomBillController
from mvc import View
from models import CustomBill, Table
from views.utils import make_button, scale_and_offset


class CustomBillView(View[CustomBillController, CustomBill]):
    """
    Renders a selectable seat layout to build a combined bill from chosen seats.
    """

    def __init__(self, root: Frame, model: CustomBill) -> None:
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
        _, seat_ids = self.draw_table()

        for ix, seat_id in enumerate(seat_ids):

            def handler(_, seat_number=ix) -> None:
                self.controller.seat_touched(seat_number)

            _ = self.__canvas.tag_bind(seat_id, "<Button-1>", handler)

        make_button(
            canvas=self.__canvas,
            text="Cancel",
            action=lambda _: self.controller.cancel(),
            location=GET_BUTTON_BOTTOM_LEFT(SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT),
        )

        if self.model.selected_seats:
            make_button(
                canvas=self.__canvas,
                text="Bill",
                action=lambda _: self.controller.bill(),
            )

    def draw_table(self, scale: float = 1) -> tuple[int, list[int]]:
        _ = self.__canvas.create_text(
            SERVER_VIEW_WIDTH // 2,
            15,
            text="Select the seats to combine Bills",
            anchor="n",
            font=("TkDefaultFont", 14, "bold"),
        )

        offset_x0, offset_y0 = SINGLE_TABLE_LOCATION
        offset_y0 += 15  # account for title

        n_seats: NumberOfSeats = self.model.table.n_seats
        seats_per_side = math.ceil(n_seats / 2)

        table_height = SEAT_DIAM * seats_per_side + SEAT_SPACING * (seats_per_side - 1)
        table_x0 = SEAT_DIAM + SEAT_SPACING

        table_bbox = scale_and_offset(
            table_x0, 0, TABLE_WIDTH, table_height, offset_x0, offset_y0, scale
        )
        table_id = self.__canvas.create_rectangle(
            *table_bbox, fill=TABLE_OUTLINE, outline=FULL_SEAT_OUTLINE
        )

        far_seat_x0 = table_x0 + TABLE_WIDTH + SEAT_SPACING

        seat_ids: list[int] = []
        for ix in range(n_seats):
            seat_x0 = (ix % 2) * far_seat_x0
            seat_y0 = (
                ix // 2 * (SEAT_DIAM + SEAT_SPACING)
                + (n_seats % 2) * (ix % 2) * (SEAT_DIAM + SEAT_SPACING) / 2
            )
            seat_bbox = scale_and_offset(
                seat_x0, seat_y0, SEAT_DIAM, SEAT_DIAM, offset_x0, offset_y0, scale
            )

            table: Table = self.model.table
            if table.has_order_for(ix):
                if self.model.is_selected(ix):
                    seat_id = self.__canvas.create_oval(
                        *seat_bbox,
                        fill=SELECTED_SEAT_FILL,
                        outline=SELECTED_SEAT_OUTLINE,
                    )
                else:
                    seat_id = self.__canvas.create_oval(
                        *seat_bbox, fill=FULL_SEAT_FILL, outline=FULL_SEAT_OUTLINE
                    )
            else:
                seat_id = self.__canvas.create_oval(
                    *seat_bbox, fill=EMPTY_SEAT_FILL, outline=EMPTY_SEAT_OUTLINE
                )

            seat_ids.append(seat_id)

        return table_id, seat_ids
