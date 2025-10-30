from typing import override
from collections.abc import Sequence
from models import Bill
from mvc import ReadRepository, WriteRepository


bills : dict[int,Bill] = []

class BillsRepository(ReadRepository[Bill, int], WriteRepository[Bill, int]):
    def __init__(self) -> None:
        super().__init__()

    @override
    def get_all(self) -> Sequence[Bill]:
        return bills

    @override
    def get_by_id(self, id: int) -> Bill | None:
        return bills.get(id)

    @override
    def create(self, item: Bill) -> int | None:
        raise Exception('dw about this rn')

    @override
    def update(self, id: int, item: Bill) -> None:
        bills[id] = item

    @override
    def delete(self, id: int) -> None:
        bills.pop(id)