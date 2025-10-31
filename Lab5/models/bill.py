from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID
from constants import TableLocation
from mvc import Model
from .menu_item import MenuItem
from typing import Literal, override
import uuid
from collections.abc import Generator
from typing import override
from mvc import ReadRepository, WriteRepository

BillsRepo: BillsRepository


class BillOrderSet:
    def __init__(
        self, table_location: TableLocation, seat_number: int, items: Sequence[MenuItem]
    ) -> None:
        self.__table_location = table_location
        self.__seat_number = seat_number
        self.__items = items

    @property
    def table_number(self) -> TableLocation:
        return self.__table_location

    @property
    def seat_number(self) -> int:
        return self.__seat_number

    @property
    def item(self) -> Sequence[MenuItem]:
        return self.__items

    @property
    def cost(self) -> float:
        return sum((item.price for item in self.__items))


class Bill(Model):
    def __init__(self, order_sets: Sequence[BillOrderSet]) -> None:
        super().__init__()
        self.__id: UUID
        self.__order_sets: Sequence[BillOrderSet] = order_sets
        self.__total: float
        self.__saved: bool = False

    @property
    def id(self) -> UUID:
        return self.__id

    @id.setter
    def id(self, id: UUID) -> None:
        self.__id = id

    @property
    def items(self) -> Sequence[BillOrderSet]:
        return self.__order_sets

    @property
    def total(self) -> float | Literal["0"]:
        return sum((order_set.cost for order_set in self.__order_sets))

    def save(self) -> None:
        if self.__saved:
            return
        print("saved bill")
        self.__id = BillsRepo.create(self)

    @override
    def __str__(self) -> str:
        return ""


class BillsSubscriber(ABC):
    @abstractmethod
    def on_update(self) -> None: ...


class BillsRepository(
    ReadRepository[Bill, uuid.UUID], WriteRepository[Bill, uuid.UUID]
):
    __bills: dict[uuid.UUID, Bill] = {}

    def __init__(self) -> None:
        super().__init__()
        self.__subscribers: list[BillsSubscriber] = []

    @override
    def get_all(self) -> Generator[Bill, None, None]:
        for value in BillsRepository.__bills.values():
            yield value

    @override
    def get_by_id(self, id: uuid.UUID) -> Bill | None:
        return BillsRepository.__bills.get(id)

    @override
    def create(self, item: Bill) -> uuid.UUID:
        id = uuid.uuid4()
        item.id = id
        BillsRepository.__bills[id] = item
        print("created bill", id, item)
        self.notify_subscribers()
        return id

    @override
    def update(self, id: uuid.UUID, item: Bill) -> None:
        BillsRepository.__bills[id] = item
        self.notify_subscribers()

    @override
    def delete(self, id: uuid.UUID) -> None:
        _ = BillsRepository.__bills.pop(id)
        self.notify_subscribers()

    def add_subscriber(self, subscriber: BillsSubscriber) -> None:
        self.__subscribers.append(subscriber)

    def notify_subscribers(self) -> None:
        for subscriber in self.__subscribers:
            subscriber.on_update()


BillsRepo = BillsRepository()
