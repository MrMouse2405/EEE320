from mvc import Model
from constants import NumberOfSeats, TableLocation
from .Order import Order


class Table(Model):
    def __init__(self, n_seats: NumberOfSeats, location: TableLocation) -> None:
        super().__init__()
        self.__n_seats: NumberOfSeats = n_seats
        self.__location: TableLocation = location
        self.__orders: list[Order] = [Order() for _ in range(n_seats)]

    @property
    def n_seats(self) -> NumberOfSeats:
        return self.__n_seats

    @property
    def location(self) -> TableLocation:
        return self.__location

    def has_any_active_orders(self) -> bool:
        for order in self.__orders:
            for item in order.items:
                if item.has_been_placed():
                    return True
        return False

    def has_order_for(self, seat: int) -> bool:
        return bool(self.__orders[seat].items)

    def order_for(self, seat: int) -> Order:
        return self.__orders[seat]
