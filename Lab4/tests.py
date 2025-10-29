import unittest
from enum import Enum, auto

from  import (
    RestaurantController,
    TableController,
    OrderController,
    KitchenController,
)
from model import MenuItem, Restaurant, OrderItem, Order, OrderState


class UI(Enum):
    """Represents the last UI drawn by the ServerViewMock."""

    RESTAURANT = auto()
    TABLE = auto()
    ORDER = auto()


class ServerViewMock:
    """A non-graphical replacement for oorms.ServerView, used for testing."""

    def __init__(self, restaurant):
        self.controller = None
        self.last_UI_created = None
        self.restaurant = restaurant
        self.set_controller(RestaurantController(self, self.restaurant))
        self.update()

    def set_controller(self, controller):
        self.controller = controller

    def update(self):
        # Simulate "redraw"
        self.controller.create_ui()

    def create_restaurant_ui(self):
        self.last_UI_created = UI.RESTAURANT

    def create_table_ui(self, table):
        self.last_UI_created = (UI.TABLE, table)

    def create_order_ui(self, order):
        self.last_UI_created = (UI.ORDER, order)


# Dummy helper to verify notify_views() was called.
class DummyView:
    def __init__(self):
        self.updated = 0

    def update(self):
        self.updated += 1


class DummyKitchenView:
    def __init__(self):
        self.updated = 0

    # KitchenController.create_ui() would call this, but our tests invoke update_order directly.
    def create_kitchen_order_ui(self):
        pass

    def update(self):
        self.updated += 1

    def set_controller(self, _):
        pass


# ---------- Original tests ----------


class OORMSTestCase(unittest.TestCase):
    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)
        self.restaurant.add_view(self.view)

    def test_initial_state(self):
        self.assertEqual(UI.RESTAURANT, self.view.last_UI_created)
        self.assertIsInstance(self.view.controller, RestaurantController)

    def test_restaurant_controller_touch_table(self):
        self.view.controller.table_touched(3)
        self.assertIsInstance(self.view.controller, TableController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[3])
        self.assertEqual(
            (UI.TABLE, self.restaurant.tables[3]), self.view.last_UI_created
        )

    def test_table_controller_done(self):
        self.view.controller.table_touched(5)
        self.view.controller.done()
        self.assertIsInstance(self.view.controller, RestaurantController)
        self.assertEqual(UI.RESTAURANT, self.view.last_UI_created)

    def test_table_controller_seat_touched(self):
        self.view.controller.table_touched(4)
        self.view.controller.seat_touched(0)
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[4])
        the_order = self.restaurant.tables[4].order_for(0)
        self.assertEqual(self.view.controller.order, the_order)
        self.assertEqual((UI.ORDER, the_order), self.view.last_UI_created)

    # Helper from the original tests
    def order_an_item(self):
        """Starting from restaurant UI, order one instance of item 0 for table 2, seat 4."""
        self.view.controller.table_touched(2)
        self.view.controller.seat_touched(4)
        the_menu_item = self.restaurant.menu_items[0]
        self.view.last_UI_created = None
        self.view.controller.add_item(the_menu_item)
        return self.restaurant.tables[2].order_for(4), the_menu_item

    def test_order_controller_add_item(self):
        the_order, the_menu_item = self.order_an_item()
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual((UI.ORDER, the_order), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertFalse(the_order.items[0].has_been_ordered())

    def test_order_controller_update_order(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.update_order()
        self.assertEqual(
            (UI.TABLE, self.restaurant.tables[2]), self.view.last_UI_created
        )
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertTrue(the_order.items[0].has_been_ordered())

    def test_order_controller_cancel(self):
        the_order, _ = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.cancel_changes()
        self.assertEqual(
            (UI.TABLE, self.restaurant.tables[2]), self.view.last_UI_created
        )
        self.assertEqual(0, len(the_order.items))

    def test_order_controller_update_several_then_cancel(self):
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        the_order = self.restaurant.tables[6].order_for(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()

        def check_first_three_items(menu_items, items):
            self.assertEqual(menu_items[0], items[0].details)
            self.assertEqual(menu_items[3], items[1].details)
            self.assertEqual(menu_items[5], items[2].details)

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        def add_two_more(menu_items, view):
            view.controller.seat_touched(7)
            view.controller.add_item(menu_items[1])
            view.controller.add_item(menu_items[2])

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.cancel_changes()

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.update_order()

        self.assertEqual(5, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)
        self.assertEqual(self.restaurant.menu_items[1], the_order.items[3].details)
        self.assertEqual(self.restaurant.menu_items[2], the_order.items[4].details)


# ------------- Lab4 Test Cases -----------


class TestOrderItemStateMachine(unittest.TestCase):
    def test_initial_and_transitions(self):
        burger = MenuItem("Burger", 10.0)
        oi = OrderItem(burger)

        # Initial state
        self.assertEqual(OrderState.REQUESTED, oi.get_order_state())
        self.assertFalse(oi.has_been_ordered())
        self.assertTrue(oi.can_be_cancelled())

        # Move to PLACED
        oi.mark_as_ordered()
        self.assertEqual(OrderState.PLACED, oi.get_order_state())
        self.assertTrue(oi.has_been_ordered())
        self.assertTrue(oi.can_be_cancelled())

        # Move to COOKING
        oi.mark_as_cooking()
        self.assertEqual(OrderState.COOKING, oi.get_order_state())
        self.assertTrue(oi.has_been_cooking())
        self.assertFalse(oi.can_be_cancelled())

        # Move to READY
        oi.mark_as_ready()
        self.assertEqual(OrderState.READY, oi.get_order_state())
        self.assertTrue(oi.has_been_ready())
        self.assertFalse(oi.can_be_cancelled())

        # Move to SERVED
        oi.mark_as_served()
        self.assertEqual(OrderState.SERVED, oi.get_order_state())
        self.assertTrue(oi.has_been_served())
        self.assertFalse(oi.can_be_cancelled())

        # Explicit cancel should put it in CANCELLED and not cancellable
        oi.mark_as_cancelled()
        self.assertEqual(OrderState.CANCELLED, oi.get_order_state())
        self.assertTrue(oi.has_been_cancelled())
        self.assertFalse(oi.can_be_cancelled())


class TestOrderBehaviours(unittest.TestCase):
    def setUp(self):
        self.restaurant = Restaurant()

    def test_add_and_total_cost(self):
        order = Order()
        m0 = MenuItem("A", 10.0)
        m1 = MenuItem("B", 14.5)
        m2 = MenuItem("C", 0.5)
        order.add_item(m0)
        order.add_item(m1)
        order.add_item(m2)
        self.assertEqual(3, len(order.items))
        self.assertAlmostEqual(25.0, order.total_cost(), places=2)

    def test_unordered_items_place_and_remove(self):
        order = Order()
        order.add_item(MenuItem("A", 10.0))  # REQUESTED
        order.add_item(MenuItem("B", 5.0))  # REQUESTED
        self.assertEqual(2, len(order.unordered_items()))

        # Place and check that there are no unordered items
        order.place_new_orders()
        self.assertEqual(0, len(order.unordered_items()))
        self.assertTrue(all(i.has_been_ordered() for i in order.items))

        # Add new REQUESTED and then remove only unordered
        order.add_item(MenuItem("C", 2.0))  # REQUESTED
        self.assertEqual(1, len(order.unordered_items()))
        order.remove_unordered_items()
        self.assertEqual(2, len(order.items))  # placed items remain

    def test_order_for_same_instance_per_seat(self):
        table = self.restaurant.tables[0]
        o0 = table.order_for(0)
        o0_again = table.order_for(0)
        self.assertIs(o0, o0_again)
        o1 = table.order_for(1)
        self.assertIsNot(o0, o1)

    def test_table_has_any_active_orders(self):
        table = self.restaurant.tables[0]
        order = table.order_for(0)
        self.assertFalse(table.has_any_active_orders())

        # Add item but not placed yet => still False
        order.add_item(self.restaurant.menu_items[0])
        self.assertFalse(table.has_any_active_orders())

        # Place => True
        order.place_new_orders()
        self.assertTrue(table.has_any_active_orders())

        # Serve => False
        order.items[0].mark_as_served()
        self.assertFalse(table.has_any_active_orders())


class TestControllersAndNotifications(unittest.TestCase):
    def setUp(self):
        self.restaurant = Restaurant()
        self.server_view = ServerViewMock(self.restaurant)
        self.restaurant.add_view(self.server_view)

    def test_cancel_item_notifies_views_and_removes(self):
        # Prepare: navigate to order and add+place one item
        self.server_view.controller.table_touched(1)
        self.server_view.controller.seat_touched(0)
        order = self.server_view.controller.order
        order.add_item(self.restaurant.menu_items[0])
        order.place_new_orders()
        item = order.items[0]
        self.assertEqual(OrderState.PLACED, item.get_order_state())

        # Add dummy observer to verify notify_views is called
        dummy = DummyView()
        self.restaurant.add_view(dummy)

        # Cancel via controller
        oc: OrderController = self.server_view.controller
        oc.cancel_item(item)

        self.assertEqual(0, len(order.items))  # removed
        self.assertGreater(dummy.updated, 0)  # notify_views invoked

    def test_kitchen_controller_progression_and_notify(self):
        # Setup: create an ordered item (PLACED)
        table = self.restaurant.tables[0]
        order = table.order_for(0)
        order.add_item(self.restaurant.menu_items[0])
        order.place_new_orders()
        item = order.items[0]
        self.assertEqual(OrderState.PLACED, item.get_order_state())

        dummy_kitchen = DummyKitchenView()
        self.restaurant.add_view(dummy_kitchen)
        kc = KitchenController(dummy_kitchen, self.restaurant)

        # PLACED -> COOKING
        kc.update_order(item)
        self.assertEqual(OrderState.COOKING, item.get_order_state())
        self.assertGreater(dummy_kitchen.updated, 0)

        # COOKING -> READY
        prev_updates = dummy_kitchen.updated
        kc.update_order(item)
        self.assertEqual(OrderState.READY, item.get_order_state())
        self.assertGreater(dummy_kitchen.updated, prev_updates)

        # READY -> SERVED
        prev_updates = dummy_kitchen.updated
        kc.update_order(item)
        self.assertEqual(OrderState.SERVED, item.get_order_state())
        self.assertGreater(dummy_kitchen.updated, prev_updates)

        # SERVED
        prev_state = item.get_order_state()
        prev_updates = dummy_kitchen.updated
        kc.update_order(item)
        self.assertEqual(prev_state, item.get_order_state())
        self.assertEqual(prev_updates + 1, dummy_kitchen.updated)  # still notifies

        # Table should have no active orders
        self.assertFalse(table.has_any_active_orders())


class Lab4TakeTableOrders(unittest.TestCase):
    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)
        self.restaurant.add_view(self.view)

    def order_an_item(self) -> tuple[Order, MenuItem]:
        self.view.controller.table_touched(2)
        self.view.controller.seat_touched(4)
        the_menu_item = self.restaurant.menu_items[0]
        self.view.last_UI_created = None
        self.view.controller.add_item(the_menu_item)
        return self.restaurant.tables[2].order_for(4), the_menu_item

    def test_check_order_state_flags(self):
        order, _ = self.order_an_item()
        # Before placing: REQUESTED
        self.assertEqual(1, len(order.items))
        self.assertFalse(order.items[0].has_been_ordered())
        self.assertTrue(order.items[0].can_be_cancelled())

        # After placing
        order.place_new_orders()
        self.assertTrue(order.items[0].has_been_ordered())
        self.assertTrue(order.items[0].can_be_cancelled())

        # After cooking starts
        order.items[0].mark_as_cooking()
        self.assertFalse(order.items[0].can_be_cancelled())


if __name__ == "__main__":
    _ = unittest.main(verbosity=2)
