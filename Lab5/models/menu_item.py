from dataclasses import dataclass
from mvc import Model


@dataclass(frozen=True)
class MenuItem(Model):
    name: str
    price: float
