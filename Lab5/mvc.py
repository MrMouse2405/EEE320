"""
EEE320 Object Oriented Programming Lab 5

Author: OCdt Syed

This file implemented generic base classes for model,
view, controller, respository, and MVCFactory (for router).

This file also implements the router file which is used to
route between different views on same window.

"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, override, TypeVar
from tkinter import Frame, Frame

"""

Interfaces are not needed, they are purely
implemented to avoid recursive types and have a sound
typed code.

Base classes are what should be used.

    # recursive types make me cry
    # I should have used Model View Intent instead, with
    # uni-directional data flow makes life so much easier!!!
    ~ Syed
"""

# ------------------------------------------------------------
# Interfaces used as *non-parameterized* bounds for TypeVars
# (Pyright doesn't allow parameterized generics in TypeVar.bound)
# ------------------------------------------------------------


class ViewInterface:
    def create_ui(self) -> None: ...
    def refresh(self) -> None: ...
    @property
    def controller(self) -> ControllerInterface: ...
    @controller.setter
    def controller(self, c: ControllerInterface) -> None: ...
    @property
    def model(self) -> ModelInterface: ...
    @model.setter
    def model(self, m: ModelInterface) -> None: ...


class ModelInterface:
    @property
    def views(self) -> Sequence[ViewInterface]: ...
    def add_views(self, view: ViewInterface) -> None: ...
    def notify_views(self) -> None: ...


class ControllerInterface:
    @property
    def view(self) -> ViewInterface: ...
    @property
    def model(self) -> ModelInterface: ...


class NavigationInterface:
    def goto(
        self, name: str, *, direction: str = "left", record_history: bool = True
    ) -> None: ...
    def go_back(self) -> None: ...
    def go_forward(self) -> None: ...


VT = TypeVar("VT", bound=ViewInterface)
MT = TypeVar("MT", bound=ModelInterface)
CT = TypeVar("CT", bound=ControllerInterface)

# ------------------------------------------------------------
# Concrete generic classes you will subclass
# We keep them generic, but we don't use parameterized bounds on TypeVars.
# ------------------------------------------------------------


class View(ABC, Frame, Generic[CT, MT], ViewInterface):
    def __init__(self, root: Frame, model: MT) -> None:
        super().__init__(master=root)
        self.__controller: CT  # set later via the property
        self.__model: MT = model
        model.add_views(self)

    @property
    def controller(self) -> CT:
        return self.__controller

    @controller.setter
    def controller(self, c: CT) -> None:
        self.__controller = c

    @property
    def model(self) -> MT:
        return self.__model

    @model.setter
    def model(self, m: MT) -> None:
        self.model = m
        m.add_views(self)

    @abstractmethod
    def create_ui(self) -> None: ...

    @abstractmethod
    def refresh(self) -> None: ...


class Model(ABC, ModelInterface):
    def __init__(self) -> None:
        super().__init__()
        self.__views: list[ViewInterface] = []

    @property
    def views(self) -> Sequence[ViewInterface]:
        return self.__views

    def add_views(self, view: ViewInterface) -> None:
        self.__views.append(view)

    def notify_views(self) -> None:
        for view in self.__views:
            view.refresh()


class Controller(ABC, Generic[VT, MT], ControllerInterface):
    def __init__(self, view: VT, model: MT) -> None:
        super().__init__()
        self.__view: VT = view
        self.__model: MT = model
        model.add_views(view)
        view.create_ui()

    @property
    def view(self) -> VT:
        return self.__view

    @view.setter
    def view(self, view: VT) -> None:
        view.create_ui()
        self.__view = view

    @property
    def model(self) -> MT:
        return self.__model

    @model.setter
    def model(self, model: MT) -> None:
        model.add_views(self.view)
        self.__model = model


# ------------------------------------------------------------
# Factory for building MVC pairs
# ------------------------------------------------------------


class MVCFactoryInterface:
    @abstractmethod
    def create(self, parent: Frame) -> VT: ...
    @abstractmethod
    def on_show(self, view: VT) -> None: ...


FT = TypeVar("FT", bound=MVCFactoryInterface)


class MVCFactory(ABC, Generic[VT, MT, CT], MVCFactoryInterface):
    """
    Builder-based factory:
      - build_model(): MT
      - build_view(parent, model): VT
      - build_controller(view, model): CT
    Caches the created trio if cache=True.
    """

    def __init__(self) -> None:
        self._model: MT
        self._view: VT
        self._controller: CT
        self._cached: bool = False

    @abstractmethod
    def build_model(self) -> MT: ...
    @abstractmethod
    def build_view(self, parent: Frame, model: MT) -> VT: ...
    @abstractmethod
    def build_controller(self, view: VT, model: MT) -> CT: ...

    @override
    def create(self, parent: Frame) -> VT:
        if self._cached:
            return self._view
        self._model = self.build_model()
        self._view = self.build_view(parent, self._model)
        self._controller = self.build_controller(self._view, self._model)
        self._view.controller = self._controller
        return self._view

    @override
    def on_show(self, view: ViewInterface) -> None:
        view.refresh()


# ------------------------------------------------------------
# Router
# ------------------------------------------------------------


class ViewRouter:
    def __init__(self, container: Frame, width: int, height: int) -> None:
        self.container = container
        self.width = width
        self.height = height
        self._factories: dict[str, MVCFactoryInterface] = {}
        self._current_name: str | None = None
        self._current_view: Frame | None = None
        self._animating = False
        self._back_stack: list[str] = []
        self._fwd_stack: list[str] = []

    def register(self, name: str, factory: MVCFactoryInterface) -> None:
        self._factories[name] = factory

    def goto(
        self, name: str, *, direction: str = "left", record_history: bool = True
    ) -> None:
        if self._animating:
            return
        factory = self._factories.get(name)
        if factory is None:
            raise KeyError(f"View '{name}' not registered")

        new_view = factory.create(self.container)
        old_view = self._current_view

        # history bookkeeping
        if record_history and self._current_name is not None:
            self._back_stack.append(self._current_name)
            self._fwd_stack.clear()

        # prepare positions
        start_x = self.width if direction == "left" else -self.width
        dx = -24 if direction == "left" else 24
        frames = max(1, (abs(start_x) // abs(dx)) + 2)

        new_view.place(x=start_x, y=0, width=self.width, height=self.height)
        new_view.lift()
        factory.on_show(new_view)

        self._animating = True

        def step(n: int) -> None:
            nonlocal new_view, old_view
            if n <= 0:
                new_view.place(x=0, y=0)
                if old_view:
                    old_view.place_forget()
                self._current_view = new_view
                self._current_name = name
                self._animating = False
                return
            new_view.place(x=new_view.winfo_x() + dx, y=0)
            if old_view:
                old_view.place(x=old_view.winfo_x() + dx, y=0)
            self.container.after(12, lambda: step(n - 1))

        if old_view:
            old_view.place(x=0, y=0, width=self.width, height=self.height)
            old_view.lift()

        step(frames)

    # Back/forward behavior (per-window)
    def can_go_back(self) -> bool:
        return bool(self._back_stack)

    def can_go_forward(self) -> bool:
        return bool(self._fwd_stack)

    def go_back(self) -> None:
        if not self._back_stack or self._current_name is None:
            return
        target = self._back_stack.pop()
        self._fwd_stack.append(self._current_name)
        self.goto(target, direction="right", record_history=False)

    def go_forward(self) -> None:
        if not self._fwd_stack or self._current_name is None:
            return
        target = self._fwd_stack.pop()
        self._back_stack.append(self._current_name)
        self.goto(target, direction="left", record_history=False)


# ------------------------------------------------------------
# Repositories
# ------------------------------------------------------------

T_co = TypeVar("T_co", covariant=True)
T = TypeVar("T")
ID = TypeVar("ID")


class ReadRepository(ABC, Generic[T_co, ID]):
    @abstractmethod
    def get_all(self) -> Sequence[T_co]: ...
    @abstractmethod
    def get_by_id(self, id: ID) -> T_co | None: ...


class WriteRepository(ABC, Generic[T, ID]):
    @abstractmethod
    def create(self, item: T) -> ID | None: ...
    @abstractmethod
    def update(self, id: ID, item: T) -> None: ...
    @abstractmethod
    def delete(self, id: ID) -> None: ...
