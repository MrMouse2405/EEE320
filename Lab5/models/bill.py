"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Model:
    Bill: Model for bill creation and saving.
    BillOrderSet: Holds orders for each seat.
                  Used for grouping multiple orders together.

CRUD:
    BillsRepository: Repository for reading / writing bills.
    BillsSubscriber: Implement this interface to recieving updates
                    from BillsRepository.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from hashlib import sha1
from typing import override
from uuid import uuid4

from constants import TableLocation
from mvc import Model, ReadRepository, WriteRepository
from .menu_item import MenuItem

type BillID = str
BillsRepo: "BillsRepository"


class BillOrderSet:
    """
    Represents a collection of orders for a single seat at a table.
    Stores seat number, table location, and ordered menu items.
    """

    def __init__(
        self,
        table_location: TableLocation,
        seat_number: int,
        items: Sequence[MenuItem],
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
    def items(self) -> Sequence[MenuItem]:
        return self.__items

    @property
    def cost(self) -> float:
        return sum(item.price for item in self.__items)


class Bill(Model):
    """
    Represents a complete customer bill composed of one or more seat orders.
    Handles bill totals and persistence through the repository.
    """

    def __init__(self, order_sets: Sequence[BillOrderSet]) -> None:
        super().__init__()
        self.__id: BillID
        self.__order_sets: Sequence[BillOrderSet] = order_sets
        self.__total: float
        self.__saved: bool = False

    @property
    def id(self) -> BillID:
        return self.__id

    @id.setter
    def id(self, id: BillID) -> None:
        self.__id = id

    @property
    def items(self) -> Sequence[BillOrderSet]:
        return self.__order_sets

    @property
    def total(self) -> float:
        return sum(order_set.cost for order_set in self.__order_sets)

    def save(self) -> None:
        if self.__saved:
            return
        self.__id = BillsRepo.create(self)

    @override
    def __str__(self) -> str:
        return ""


class BillsSubscriber(ABC):
    """
    Defines an interface for subscribers that react to repository updates.
    Implemented by classes that need notification on bill data changes.
    """

    @abstractmethod
    def on_update(self) -> None: ...


class BillsRepository(ReadRepository[Bill, str], WriteRepository[Bill, BillID]):
    """
    In-memory repository for managing Bill objects.
    Provides CRUD operations and notifies subscribers on data changes.
    """

    __bills: dict[BillID, Bill] = {}

    def __init__(self) -> None:
        super().__init__()
        self.__subscribers: list[BillsSubscriber] = []

    @override
    def get_all(self) -> Generator[Bill, None, None]:
        for value in BillsRepository.__bills.values():
            yield value

    @override
    def get_by_id(self, id: BillID) -> Bill | None:
        return BillsRepository.__bills.get(id)

    @override
    def create(self, item: Bill) -> BillID:
        id: str = sha1(uuid4().bytes).hexdigest()[:8]
        item.id = id
        BillsRepository.__bills[id] = item
        self.notify_subscribers()
        return id

    @override
    def update(self, id: BillID, item: Bill) -> None:
        BillsRepository.__bills[id] = item
        self.notify_subscribers()

    @override
    def delete(self, id: BillID) -> None:
        _ = BillsRepository.__bills.pop(id)
        self.notify_subscribers()

    def add_subscriber(self, subscriber: BillsSubscriber) -> None:
        self.__subscribers.append(subscriber)

    def notify_subscribers(self) -> None:
        for subscriber in self.__subscribers:
            subscriber.on_update()


BillsRepo = BillsRepository()
