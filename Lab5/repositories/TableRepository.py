from typing import override
from mvc import ReadRepository
from models import Table
from constants import TableLocation, TABLES


class TableRepository(ReadRepository[Table, TableLocation]):
    def __init__(self) -> None:
        super().__init__()
        self.__tables: list[Table] = [
            Table(seats, location) for seats, location in TABLES
        ]

    @override
    def get_all(self) -> list[Table]:
        return self.__tables

    @override
    def get_by_id(self, id: TableLocation) -> Table | None:
        for table in self.__tables:
            if table.location == id:
                return table
        return None
