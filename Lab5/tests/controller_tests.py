"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Tests all controllers.
"""

import unittest
from typing import Any

# Models
from models import (
    Bill,
    BillOrderSet,
    CustomBill,
    MenuItem,
    Order,
    OrderItem,
    Printer,
    Restaurant,
    Table,
)
from models.bill import BillsRepository, BillsSubscriber

# Controllers
from controllers import (
    BillController,
    CustomBillController,
    OrderController,
    PrinterController,
    ServerController,
    TableController,
)

# -------------------- Test Fakes --------------------


class FakeRouter:
    """Duck-typed ViewRouter used by controllers in tests."""

    def __init__(self) -> None:
        self.goto_calls: list[tuple[str, dict[str, Any]]] = []
        self.go_back_calls: int = 0

    def goto(self, name: str, *_, **kwargs) -> None:
        self.goto_calls.append((name, kwargs))

    def go_back(self) -> None:
        self.go_back_calls += 1


class FakeServerView:
    """Minimal server view: controllers expect create_ui() and create_restaurant_ui()."""

    def __init__(self) -> None:
        self.created_ui = False
        self.created_restaurant = False

    def create_ui(self) -> None:
        self.created_ui = True

    def create_restaurant_ui(self) -> None:
        self.created_restaurant = True


class FakeView:
    """Generic fake view: must provide create_ui() to satisfy Controller.__init__."""

    def __init__(self) -> None:
        self.created_ui = False

    def create_ui(self) -> None:
        self.created_ui = True


# -------------------- Shared Utilities --------------------


class DummySubscriber(BillsSubscriber):
    def __init__(self) -> None:
        self.count = 0

    def on_update(self) -> None:
        self.count += 1


def fresh_bills_repo_patch():
    """Clear class-level storage and return a fresh repo bound to models.bill.BillsRepo."""
    import models.bill as bill_module

    BillsRepository._BillsRepository__bills.clear()
    repo = BillsRepository()
    bill_module.BillsRepo = repo
    return repo


# -------------------- Controller Tests --------------------


class TestServerController(unittest.TestCase):
    def test_initializes_view_and_navigates_to_table(self):
        view = FakeServerView()
        model = Restaurant()
        router = FakeRouter()
        ctrl = ServerController(view, model, router)

        # The base Controller calls create_ui(); ServerController also calls create_restaurant_ui()
        self.assertTrue(
            view.created_ui, "create_ui() should be called by base Controller"
        )
        self.assertTrue(
            view.created_restaurant,
            "create_restaurant_ui() should be called by ServerController",
        )

        ctrl.on_table_touch(0)
        self.assertEqual(len(router.goto_calls), 1)
        name, kwargs = router.goto_calls[0]
        self.assertEqual(name, "table")
        self.assertIs(kwargs.get("payload"), model.tables[0])


class TestTableController(unittest.TestCase):
    def setUp(self) -> None:
        self.table = Table(3, (10, 20))
        self.table.order_for(0).add_item(MenuItem("A", 1.0))
        self.table.order_for(2).add_item(MenuItem("B", 2.0))
        self.router = FakeRouter()
        self.ctrl = TableController(FakeView(), self.table, self.router)
        self.repo = fresh_bills_repo_patch()

    def test_seat_touched_navigates_to_order(self):
        self.ctrl.seat_touched(2)
        self.assertEqual(len(self.router.goto_calls), 1)
        name, kwargs = self.router.goto_calls[0]
        self.assertEqual(name, "order")
        self.assertIs(kwargs.get("payload"), self.table.order_for(2))

    def test_bill_table_creates_single_bill_clears_orders_and_go_back(self):
        self.ctrl.bill_table()
        bills = list(self.repo.get_all())
        self.assertEqual(len(bills), 1)
        bill = bills[0]
        self.assertEqual(len(list(bill.items)), self.table.n_seats)
        self.assertTrue(all(len(o.items) == 0 for o in self.table.orders))
        self.assertEqual(self.router.go_back_calls, 1)

    def test_bill_seats_creates_bills_per_non_empty_order_then_clears_and_back(self):
        self.ctrl.bill_seats()
        bills = list(self.repo.get_all())
        self.assertEqual(len(bills), 2)
        self.assertTrue(all(len(o.items) == 0 for o in self.table.orders))
        self.assertEqual(self.router.go_back_calls, 1)

    def test_bill_custom_navigates_with_custom_bill_payload(self):
        self.ctrl.bill_custom()
        self.assertEqual(len(self.router.goto_calls), 1)
        name, kwargs = self.router.goto_calls[0]
        self.assertEqual(name, "custom_bill")
        payload = kwargs.get("payload")
        self.assertIsInstance(payload, CustomBill)
        self.assertIs(payload.table, self.table)


class TestOrderController(unittest.TestCase):
    def setUp(self) -> None:
        self.order = Order()
        self.router = FakeRouter()
        self.ctrl = OrderController(FakeView(), self.order, self.router)

    def test_add_and_remove_items(self):
        mi1 = MenuItem("X", 1.0)
        self.ctrl.add_item(mi1)
        self.assertEqual(len(self.order.items), 1)
        oi = next(iter(self.order.items))
        self.assertIsInstance(oi, OrderItem)

        self.ctrl.remove(oi)
        self.assertEqual(len(self.order.items), 0)

    def test_cancel_changes_removes_requested_and_goes_back(self):
        self.ctrl.add_item(MenuItem("A", 1.0))
        self.assertEqual(len(list(self.order.requested_items)), 1)
        self.ctrl.cancel_changes()
        self.assertEqual(len(self.order.items), 0)
        self.assertEqual(self.router.go_back_calls, 1)

    def test_update_order_places_and_goes_back(self):
        self.ctrl.add_item(MenuItem("A", 1.0))
        self.ctrl.update_order()
        self.assertEqual(len(list(self.order.requested_items)), 0)
        self.assertEqual(len(self.order.items), 1)
        self.assertTrue(all(i.has_been_placed() for i in self.order.items))
        self.assertEqual(self.router.go_back_calls, 1)


class TestPrinterController(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = fresh_bills_repo_patch()
        bos = BillOrderSet((0, 0), 0, [MenuItem("C", 3.0)])
        b = Bill([bos])
        b.save()
        self.printer = Printer()
        self.router = FakeRouter()
        self.ctrl = PrinterController(FakeView(), self.printer, self.router)
        self.bill_id = b.id

    def test_navigate_to_bill_payload(self):
        self.ctrl.on_bill_touched(self.bill_id)
        self.assertEqual(len(self.router.goto_calls), 1)
        name, kwargs = self.router.goto_calls[0]
        self.assertEqual(name, "bill")
        payload = kwargs.get("payload")
        self.assertIsInstance(payload, Bill)
        self.assertEqual(payload.id, self.bill_id)


class TestBillController(unittest.TestCase):
    def test_done_goes_back(self):
        bos = BillOrderSet((0, 0), 0, [MenuItem("I", 1.0)])
        bill = Bill([bos])
        router = FakeRouter()
        ctrl = BillController(FakeView(), bill, router)
        ctrl.done()
        self.assertEqual(router.go_back_calls, 1)


class TestCustomBillController(unittest.TestCase):
    def setUp(self) -> None:
        self.table = Table(3, (0, 0))
        self.table.order_for(0).add_item(MenuItem("M0", 1.0))
        self.table.order_for(1).add_item(MenuItem("M1", 2.0))
        self.model = CustomBill(self.table)
        self.router = FakeRouter()
        self.repo = fresh_bills_repo_patch()
        self.ctrl = CustomBillController(FakeView(), self.model, self.router)

    def test_seat_touched_toggles_selection_only_for_valid_seats_with_orders(self):
        self.ctrl.seat_touched(0)
        self.assertTrue(self.model.is_selected(0))
        self.ctrl.seat_touched(0)
        self.assertFalse(self.model.is_selected(0))
        self.ctrl.seat_touched(2)
        self.assertFalse(self.model.is_selected(2))

    def test_bill_creates_one_bill_for_selected_seats_clears_and_back(self):
        self.model.add_selected_seat(0)
        self.model.add_selected_seat(1)
        self.ctrl.bill()
        bills = list(self.repo.get_all())
        self.assertEqual(len(bills), 1)
        bill = bills[0]
        self.assertEqual(len(list(bill.items)), 2)
        self.assertEqual(len(self.table.order_for(0).items), 0)
        self.assertEqual(len(self.table.order_for(1).items), 0)
        self.assertEqual(self.router.go_back_calls, 1)

    def test_cancel_clears_selection_and_back(self):
        self.model.add_selected_seat(0)
        self.ctrl.cancel()
        self.assertEqual(len(self.model.selected_seats), 0)
        self.assertEqual(self.router.go_back_calls, 1)


# -------------------- Suite Builder --------------------


def ControllersTestSuite() -> unittest.TestSuite:
    s = unittest.TestSuite()
    loader = unittest.defaultTestLoader
    s.addTests(loader.loadTestsFromTestCase(TestServerController))
    s.addTests(loader.loadTestsFromTestCase(TestTableController))
    s.addTests(loader.loadTestsFromTestCase(TestOrderController))
    s.addTests(loader.loadTestsFromTestCase(TestPrinterController))
    s.addTests(loader.loadTestsFromTestCase(TestBillController))
    s.addTests(loader.loadTestsFromTestCase(TestCustomBillController))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(ControllersTestSuite())
