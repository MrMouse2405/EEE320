"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Runs all test suites.
"""

import unittest
from tests import MVCTestSuite, ModelsTestSuite
from tests import ControllersTestSuite

if __name__ == "__main__":
    all_suites = unittest.TestSuite(
        [ModelsTestSuite(), ControllersTestSuite(), MVCTestSuite()]
    )
    _ = unittest.TextTestRunner(verbosity=2).run(all_suites)
