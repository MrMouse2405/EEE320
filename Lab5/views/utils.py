"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Utilities:
    Canvas helpers for drawing tables and buttons, with scaling and positioning.
"""

import math
from typing import Callable
from tkinter import Canvas

from constants import (
    BUTTON_SIZE,
    BUTTON_STYLE_FILL,
    BUTTON_STYLE_OUTLINE,
    BUTTON_TEXT_STYLE_FILL,
    CANCEL_STYLE_FILL,
    EMPTY_SEAT_FILL,
    EMPTY_SEAT_OUTLINE,
    FULL_SEAT_FILL,
    FULL_SEAT_OUTLINE,
    GET_BUTTON_BOTTOM_RIGHT,
    SEAT_DIAM,
    SEAT_SPACING,
    SERVER_VIEW_HEIGHT,
    SERVER_VIEW_WIDTH,
    TABLE_FILL,
    TABLE_OUTLINE,
    TABLE_WIDTH,
    TableLocation,
)
from models import Table


def scale_and_offset(
    x0: float,
    y0: float,
    width: float,
    height: float,
    offset_x0: float,
    offset_y0: float,
    scale: float,
) -> tuple[float, float, float, float]:
    return (
        (offset_x0 + x0) * scale,
        (offset_y0 + y0) * scale,
        (offset_x0 + x0 + width) * scale,
        (offset_y0 + y0 + height) * scale,
    )


def draw_table(
    canvas: Canvas,
    table: Table,
    location: TableLocation | None = None,
    scale: float = 1,
) -> tuple[int, list[int]]:
    offset_x0, offset_y0 = location if location else table.location
    seats_per_side = math.ceil(table.n_seats / 2)
    table_height = SEAT_DIAM * seats_per_side + SEAT_SPACING * (seats_per_side - 1)
    table_x0 = SEAT_DIAM + SEAT_SPACING

    table_bbox = scale_and_offset(
        table_x0, 0, TABLE_WIDTH, table_height, offset_x0, offset_y0, scale
    )
    table_id = canvas.create_rectangle(
        *table_bbox, fill=TABLE_FILL, outline=TABLE_OUTLINE
    )

    far_seat_x0 = table_x0 + TABLE_WIDTH + SEAT_SPACING

    seat_ids: list[int] = []
    for ix in range(table.n_seats):
        seat_x0 = (ix % 2) * far_seat_x0
        seat_y0 = (
            ix // 2 * (SEAT_DIAM + SEAT_SPACING)
            + (table.n_seats % 2) * (ix % 2) * (SEAT_DIAM + SEAT_SPACING) / 2
        )
        seat_bbox = scale_and_offset(
            seat_x0, seat_y0, SEAT_DIAM, SEAT_DIAM, offset_x0, offset_y0, scale
        )

        if table.has_order_for(ix):
            seat_id = canvas.create_oval(
                *seat_bbox, fill=FULL_SEAT_FILL, outline=FULL_SEAT_OUTLINE
            )
        else:
            seat_id = canvas.create_oval(
                *seat_bbox, fill=EMPTY_SEAT_FILL, outline=EMPTY_SEAT_OUTLINE
            )

        seat_ids.append(seat_id)

    return table_id, seat_ids


_DEFAULT_BUTTON_LOCATION = GET_BUTTON_BOTTOM_RIGHT(
    SERVER_VIEW_WIDTH, SERVER_VIEW_HEIGHT
)


def make_button(
    canvas: Canvas,
    text: str,
    action: Callable[..., None],
    size: tuple[int, int] = BUTTON_SIZE,
    location: tuple[int, int] = _DEFAULT_BUTTON_LOCATION,
    fill: str = BUTTON_STYLE_FILL,
    outline: str = BUTTON_STYLE_OUTLINE,
) -> None:
    w, h = size
    x0, y0 = location
    box = canvas.create_rectangle(x0, y0, x0 + w, y0 + h, fill=fill, outline=outline)
    label = canvas.create_text(
        x0 + w / 2, y0 + h / 2, text=text, fill=BUTTON_TEXT_STYLE_FILL
    )
    _ = canvas.tag_bind(box, "<Button-1>", action)
    _ = canvas.tag_bind(label, "<Button-1>", action)
