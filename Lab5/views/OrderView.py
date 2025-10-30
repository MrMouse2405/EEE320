"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

"""

from tkinter import Frame
from typing import override
from controllers import OrderController
from models import Order
from mvc import View


class OrderView(View[OrderController, Order]):
    def __init__(self, root: Frame, model: Order) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
