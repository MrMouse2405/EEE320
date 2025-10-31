"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from mvc import View
from controllers import BillController
from models import Bill
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


from views.utils import make_button


class BillView(View[BillController, Bill]):
    def __init__(self, root: Frame, model: Bill) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")
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
        self.create_bill_ui()

    def create_bill_ui(self) -> None: ...
