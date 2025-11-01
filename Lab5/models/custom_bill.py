"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

CustomBill:
    Used for group billing across multiple seats at a table.
"""

from collections.abc import Sequence
from mvc import Model
from constants import SeatNumber
from .table import Table


class CustomBill(Model):
    """
    Represents a temporary or user-defined bill for a single table.
    Tracks which seats are selected for merging or combined billing.
    """

    def __init__(self, table: Table) -> None:
        super().__init__()
        self.__table = table
        self.__selected_seats: list[SeatNumber] = []

    @property
    def table(self) -> Table:
        return self.__table

    def add_selected_seat(self, seat_number: SeatNumber) -> None:
        assert seat_number >= 0 or seat_number <= self.__table.n_seats
        if seat_number not in self.__selected_seats:
            self.__selected_seats.append(seat_number)
            self.notify_views()

    def remove_selected_seat(self, seat_number: SeatNumber) -> None:
        if seat_number in self.__selected_seats:
            self.__selected_seats.remove(seat_number)
            self.notify_views()

    def is_selected(self, seat_number: SeatNumber) -> bool:
        return seat_number in self.__selected_seats

    def remove_all_selected_seats(self) -> None:
        self.__selected_seats.clear()
        self.notify_views()

    @property
    def selected_seats(self) -> Sequence[SeatNumber]:
        return self.__selected_seats
