"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

MenuItem Model
"""

from dataclasses import dataclass
from mvc import Model


@dataclass(frozen=True)
class MenuItem(Model):
    """
    Represents a menu item with a fixed name and price.
    Used as an immutable data model within the billing system.
    """

    name: str
    price: float
