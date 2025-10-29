from tkinter import Tk
from typing import override
from controllers import OrderController
from models import Order
from mvc import View


class OrderView(View[OrderController, Order]):
    def __init__(self, root: Tk, model: Order) -> None:
        super().__init__(root, model)

    @override
    def create_ui(self) -> None:
        print("create_ui")

    @override
    def refresh(self) -> None:
        print("refresh")
