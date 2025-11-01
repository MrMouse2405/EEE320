"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Printer:
    Acts as a subscriber to the BillsRepository.
    Provides access to all bills and updates views when repository data changes.
"""

from collections.abc import Generator
from typing import override
from mvc import Model
from .bill import Bill, BillID, BillsRepo, BillsSubscriber


class Printer(Model, BillsSubscriber):
    """
    Represents a printing component that observes bill updates.
    Subscribes to the repository and refreshes views when bills change.
    """

    def __init__(self) -> None:
        super().__init__()
        BillsRepo.add_subscriber(self)

    @property
    def bills(self) -> Generator[Bill]:
        return BillsRepo.get_all()

    def get_bill_by_id(self, id: BillID) -> Bill | None:
        return BillsRepo.get_by_id(id)

    @override
    def on_update(self) -> None:
        return self.notify_views()
