"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Tests all models.
"""

import unittest
from dataclasses import is_dataclass, FrozenInstanceError

from models import (
    Restaurant,
    Table,
    Printer,
    Order,
    OrderItem,
    Bill,
    BillOrderSet,
    BillsRepository,
    BillsSubscriber,
    CustomBill,
    MenuItem,
)

from constants import MENU_ITEMS, TABLES, TableLocation


# -------------------- Utilities --------------------


class DummySubscriber(BillsSubscriber):
    def __init__(self) -> None:
        self.count = 0

    def on_update(self) -> None:
        self.count += 1


# -------------------- Model Tests --------------------


class TestMenuItem(unittest.TestCase):
    def test_menu_item_is_dataclass_and_frozen(self):
        self.assertTrue(is_dataclass(MenuItem))
        item = MenuItem("Coffee", 2.5)
        with self.assertRaises(FrozenInstanceError):
            item.price = 3.0


class TestOrderItem(unittest.TestCase):
    def test_state_transitions(self):
        mi = MenuItem("Tea", 2.0)
        oi = OrderItem(mi)
        self.assertFalse(oi.has_been_placed())
        self.assertFalse(oi.has_been_billed())
        self.assertTrue(oi.can_be_cancelled())

        oi.mark_as_placed()
        self.assertTrue(oi.has_been_placed())
        self.assertFalse(oi.has_been_billed())

        oi.mark_as_billed()
        self.assertTrue(oi.has_been_billed())
        self.assertFalse(oi.can_be_cancelled())


class TestOrder(unittest.TestCase):
    def test_add_remove_and_total(self):
        order = Order()
        mi_list = list(order.menu_items)
        self.assertEqual(len(mi_list), len(MENU_ITEMS))

        a = MenuItem("A", 3.0)
        b = MenuItem("B", 4.5)
        order.add_item(a)
        order.add_item(b)
        self.assertEqual(len(order.items), 2)
        self.assertAlmostEqual(order.total_cost, 7.5, places=2)

        to_remove = next(i for i in order.items if i.details.name == "A")
        order.remove_item(to_remove)
        self.assertEqual(len(order.items), 1)
        self.assertAlmostEqual(order.total_cost, 4.5, places=2)

    def test_place_and_cancel_requested(self):
        order = Order()
        x = MenuItem("X", 1.0)
        y = MenuItem("Y", 2.0)
        order.add_item(x)
        order.add_item(y)

        self.assertEqual(len(list(order.requested_items)), 2)
        order.place_new_orders()
        self.assertEqual(len(list(order.requested_items)), 0)
        self.assertTrue(all(item.has_been_placed() for item in order.items))

        z = MenuItem("Z", 3.0)
        order.add_item(z)
        self.assertEqual(len(list(order.requested_items)), 1)
        order.remove_requested_items()
        self.assertEqual(len(order.items), 2)
        order.clear()
        self.assertEqual(len(order.items), 0)


class TestTable(unittest.TestCase):
    def test_table_orders_and_activity(self):
        location: TableLocation = (10, 20)
        table = Table(3, location)
        self.assertEqual(table.n_seats, 3)
        self.assertEqual(table.location, location)
        self.assertFalse(table.has_any_active_orders())

        order = table.order_for(1)
        order.add_item(MenuItem("Soup", 5.0))
        self.assertTrue(table.has_order_for(1))
        self.assertFalse(table.has_any_active_orders())

        order.place_new_orders()
        self.assertTrue(table.has_any_active_orders())

        table.clear_orders()
        self.assertFalse(table.has_any_active_orders())
        self.assertTrue(all(len(o.items) == 0 for o in table.orders))


class TestRestaurant(unittest.TestCase):
    def test_restaurant_initialization_matches_constants(self):
        r = Restaurant()
        self.assertEqual(len(r.tables), len(TABLES))
        self.assertEqual(len(r.menu_items), len(MENU_ITEMS))


class TestBillAndRepository(unittest.TestCase):
    def setUp(self) -> None:
        import models.bill as bill_module

        self.repo = BillsRepository()
        BillsRepository._BillsRepository__bills.clear()
        bill_module.BillsRepo = self.repo

    def test_bill_order_set_and_total(self):
        items = [MenuItem("Noodles", 8.0), MenuItem("Drink", 2.5)]
        bos = BillOrderSet(table_location=(0, 0), seat_number=1, items=items)
        bill = Bill([bos])
        self.assertAlmostEqual(bill.total, 10.5, places=2)

        sub = DummySubscriber()
        self.repo.add_subscriber(sub)
        bill.save()
        self.assertIsNotNone(bill.id)
        self.assertEqual(sub.count, 1)

        all_bills = list(self.repo.get_all())
        self.assertTrue(any(b.id == bill.id for b in all_bills))
        self.assertIs(self.repo.get_by_id(bill.id), bill)

    def test_multiple_bills_and_delete_update(self):
        sub = DummySubscriber()
        self.repo.add_subscriber(sub)

        def mkbill(seat, total):
            bos = BillOrderSet(
                table_location=(1, 1),
                seat_number=seat,
                items=[MenuItem("X", total)],
            )
            b = Bill([bos])
            b.save()
            return b

        b1 = mkbill(1, 5.0)
        b2 = mkbill(2, 7.5)
        self.assertGreaterEqual(sub.count, 2)

        self.repo.update(b1.id, b1)
        self.assertGreaterEqual(sub.count, 3)

        self.repo.delete(b2.id)
        self.assertGreaterEqual(sub.count, 4)
        self.assertIsNone(self.repo.get_by_id(b2.id))


class TestCustomBill(unittest.TestCase):
    def test_selection_flow(self):
        table = Table(4, (5, 5))
        table.order_for(0).add_item(MenuItem("A", 1.0))
        table.order_for(2).add_item(MenuItem("B", 2.0))
        cb = CustomBill(table)

        cb.add_selected_seat(0)
        cb.add_selected_seat(2)
        self.assertTrue(cb.is_selected(0))
        self.assertTrue(cb.is_selected(2))
        self.assertEqual(set(cb.selected_seats), {0, 2})

        cb.remove_selected_seat(0)
        self.assertFalse(cb.is_selected(0))
        self.assertTrue(cb.is_selected(2))

        cb.remove_all_selected_seats()
        self.assertEqual(len(cb.selected_seats), 0)


class TestPrinterModel(unittest.TestCase):
    def setUp(self) -> None:
        import models.bill as bill_module

        self.repo = BillsRepository()
        BillsRepository._BillsRepository__bills.clear()
        bill_module.BillsRepo = self.repo
        from models import Printer  # Import after monkeypatch

        self.Printer = Printer

    def test_printer_subscribes_and_exposes_bills(self):
        printer = self.Printer()
        self.assertEqual(list(printer.bills), [])
        bos = BillOrderSet((0, 0), 0, [MenuItem("C", 3.0)])
        b = Bill([bos])
        b.save()
        self.assertEqual(len(list(printer.bills)), 1)


# -------------------- Suite Builder --------------------


def ModelsTestSuite() -> unittest.TestSuite:
    suite = unittest.TestSuite()
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestMenuItem))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestOrderItem))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestOrder))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestTable))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestRestaurant))
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromTestCase(TestBillAndRepository)
    )
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestCustomBill))
    suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(TestPrinterModel))
    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(ModelsTestSuite())
