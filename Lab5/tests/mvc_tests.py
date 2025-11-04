"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed, OCdt Pabon-Gonzalez

Tests core classes.
"""

import unittest
from typing import Any, Optional

from mvc import (
    ControllerInterface,
    Model,
    Controller,
    MVCFactory,
    ViewRouter,
    ViewInterface,
    MVCFactoryInterface,
)


# -------------------- Fakes --------------------


class FakeView(ViewInterface):
    """Minimal view satisfying ViewInterface for controller/model tests."""

    def __init__(self) -> None:
        self.created = False
        self.refreshed = 0
        self._controller: Optional[ControllerInterface] = None
        self._model: Optional[Model] = None

    def create_ui(self) -> None:
        self.created = True

    def refresh(self) -> None:
        self.refreshed += 1

    @property
    def controller(self) -> ControllerInterface:
        assert self._controller is not None
        return self._controller

    @controller.setter
    def controller(self, c: ControllerInterface) -> None:
        self._controller = c

    @property
    def model(self) -> Model:
        assert self._model is not None
        return self._model

    @model.setter
    def model(self, m: Model) -> None:
        self._model = m


class FakeContainer:
    """Widget-like container with after() for ViewRouter; calls immediately."""

    def after(self, _ms: int, fn) -> None:
        fn()


class FakeWidget:
    """Widget-like object returned by factories for ViewRouter navigation."""

    def __init__(self) -> None:
        self._x = 0
        self.placed = []
        self.lifted = 0
        self.forgotten = 0

    # Tk-like API used by ViewRouter
    def place(self, **kwargs) -> None:
        # record and track x for winfo_x()
        self.placed.append(kwargs)
        if "x" in kwargs:
            self._x = kwargs["x"]

    def lift(self) -> None:
        self.lifted += 1

    def place_forget(self) -> None:
        self.forgotten += 1

    def winfo_x(self) -> int:
        return int(self._x)


class FakeFactory(MVCFactoryInterface):
    """Direct MVCFactoryInterface for router tests (no dependency on MVCFactory base)."""

    def __init__(self) -> None:
        self.created = 0
        self.on_show_calls = 0
        self.last_view: Optional[FakeWidget] = None
        self.next_view: Optional[FakeWidget] = None  # allow deterministic view return

    def create(self, parent, payload) -> FakeWidget:
        self.created += 1
        self.last_view = self.next_view or FakeWidget()
        return self.last_view

    def on_show(self, view) -> None:
        self.on_show_calls += 1
        # mimic MVCFactory.on_show(view) behavior by calling refresh() when available
        if hasattr(view, "refresh"):
            view.refresh()


# -------------------- Model / Controller / Factory tests --------------------


class TestModelViewNotify(unittest.TestCase):
    def test_add_views_and_notify(self):
        m = Model()
        v1, v2 = FakeView(), FakeView()
        m.add_views(v1)
        m.add_views(v2)
        m.add_views(v1)  # idempotent
        self.assertEqual(len(m.views), 2)
        m.notify_views()
        self.assertEqual(v1.refreshed, 1)
        self.assertEqual(v2.refreshed, 1)


class TestControllerWiring(unittest.TestCase):
    class _C(Controller[FakeView, Model]):  # generic param types are nominal here
        pass

    def test_controller_sets_view_controller_and_calls_create_ui(self):
        m = Model()
        v = FakeView()
        nav = object()  # not used by base Controller
        _ = self._C(v, m, nav)  # base ctor does the wiring
        self.assertIs(v.controller, _)  # type: ignore[arg-type]
        self.assertTrue(
            v.created, "create_ui() should be called by Controller.__init__"
        )


class TestMVCFactoryCaching(unittest.TestCase):
    class _Factory(MVCFactory[FakeView, Model, ControllerInterface]):
        def __init__(self, navigation):
            super().__init__(navigation)
            self.built = {"model": 0, "view": 0, "controller": 0}

        def build_model(self) -> Model:
            self.built["model"] += 1
            return Model()

        def build_view(self, parent, model) -> FakeView:
            self.built["view"] += 1
            v = FakeView()
            v.model = model
            return v

        def build_controller(self, view, model, navigation) -> ControllerInterface:
            self.built["controller"] += 1

            # Minimal no-op controller
            class _C(Controller[FakeView, Model]): ...

            return _C(view, model, navigation)

    def test_create_caches_without_payload_and_rebuilds_with_payload(self):
        nav = object()
        fac = self._Factory(nav)
        parent = object()

        # First create (no payload) -> builds all
        v1 = fac.create(parent, payload=None)
        self.assertEqual(fac.built, {"model": 1, "view": 1, "controller": 1})

        # Second create (no payload) -> cached view returned
        v2 = fac.create(parent, payload=None)
        self.assertIs(v1, v2)
        self.assertEqual(fac.built, {"model": 1, "view": 1, "controller": 1})

        # Third create (with payload) -> forced rebuild
        v3 = fac.create(parent, payload=Model())
        self.assertIsNot(v1, v3)
        self.assertEqual(fac.built, {"model": 1, "view": 2, "controller": 2})


# -------------------- Router tests --------------------


class TestViewRouter(unittest.TestCase):
    def setUp(self) -> None:
        self.container = FakeContainer()
        self.router = ViewRouter(self.container, width=120, height=80)
        self.factory_a = FakeFactory()
        self.factory_b = FakeFactory()
        self.router.register("A", self.factory_a)
        self.router.register("B", self.factory_b)

    def test_goto_sets_current_and_calls_on_show(self):
        self.router.goto("A")
        # on_show should have been called
        self.assertEqual(self.factory_a.on_show_calls, 1)
        # next navigation pushes history
        self.router.goto("B")
        self.assertEqual(self.factory_b.on_show_calls, 1)
        self.assertTrue(self.router.can_go_back())
        self.assertFalse(self.router.can_go_forward())

        # go_back then go_forward restore as expected
        self.router.go_back()
        self.assertTrue(self.router.can_go_forward())
        self.router.go_forward()
        self.assertTrue(self.router.can_go_back())

    def test_goto_unregistered_raises(self):
        with self.assertRaises(KeyError):
            self.router.goto("NOPE")

    def test_animating_guard_noop(self):
        # Simulate animating lock
        self.router._animating = True  # type: ignore[attr-defined]
        # No KeyError, no on_show
        self.router.goto("A")
        self.assertEqual(self.factory_a.on_show_calls, 0)


# -------------------- Suite builder --------------------


def MVCTestSuite() -> unittest.TestSuite:
    s = unittest.TestSuite()
    L = unittest.defaultTestLoader
    s.addTests(L.loadTestsFromTestCase(TestModelViewNotify))
    s.addTests(L.loadTestsFromTestCase(TestControllerWiring))
    s.addTests(L.loadTestsFromTestCase(TestMVCFactoryCaching))
    s.addTests(L.loadTestsFromTestCase(TestViewRouter))
    return s


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(MVCTestSuite())
