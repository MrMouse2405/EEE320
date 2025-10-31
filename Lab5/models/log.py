from collections.abc import Generator, Sequence
from mvc import Model
from .bill import Bill, BillsRepo, BillsSubscriber
from typing import override


class Log(Model, BillsSubscriber):
    def __init__(self):
        super().__init__()

    @property
    def get_all_bills(self) -> Generator[Bill]:
        return BillsRepo.get_all()

    @override
    def on_update(self) -> None:
        self.notify_views()
