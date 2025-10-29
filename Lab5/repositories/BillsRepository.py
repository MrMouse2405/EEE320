from typing import override
from collections.abc import Sequence
from models import Bill
from mvc import ReadRepository, WriteRepository


class BillsRepository(ReadRepository[Bill, int], WriteRepository[Bill, int]):
    def __init__(self) -> None:
        super().__init__()

    @override
    def get_all(self) -> Sequence[Bill]:
        return []

    @override
    def get_by_id(self, id: int) -> Bill | None:
        return None

    @override
    def create(self, item: Bill) -> int | None:
        return None

    @override
    def update(self, id: int, item: Bill) -> None: ...

    @override
    def delete(self, id: int) -> None: ...
