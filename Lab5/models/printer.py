from collections.abc import Generator
from typing import override
from uuid import UUID
from mvc import Model
from .bill import Bill, BillsRepo, BillsSubscriber


class Printer(Model, BillsSubscriber):
    def __init__(self) -> None:
        super().__init__()
        BillsRepo.add_subscriber(self)

    @property
    def bills(self) -> Generator[Bill]:
        return BillsRepo.get_all()

    def get_bill_by_id(self, id: UUID) -> Bill | None:
        return BillsRepo.get_by_id(id)

    @override
    def on_update(self) -> None:
        return self.notify_views()
