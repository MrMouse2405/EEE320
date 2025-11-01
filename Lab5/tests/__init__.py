"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Exports:
    Public-facing classes for the models package.
"""

from .model_tests import ModelsTestSuite
from .controller_tests import ControllersTestSuite
from .mvc_tests import MVCTestSuite

__all__ = ["ModelsTestSuite", "ControllersTestSuite", "MVCTestSuite"]
