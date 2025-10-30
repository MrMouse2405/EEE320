from mvc import Model
from models import MenuItem
from typing import Sequence

class Bill(Model):
    def __init__(self, items: Sequence[MenuItem]) -> None:
        super().__init__()
        self.__idBill: int
        self.__tableNbr: int
        self.__items: Sequence[MenuItem] = items
        self.__total: float
