from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, Protocol, TypeVar
from tkinter import Tk, Frame

# ------------------------------------------------------------
# Protocols used as *non-parameterized* bounds for TypeVars
# (Pyright doesn't allow parameterized generics in TypeVar.bound)
# ------------------------------------------------------------


class ViewProto(Protocol):
    def create_ui(self) -> None: ...
    def refresh(self) -> None: ...


class ModelProto(Protocol):
    @property
    def views(self) -> Sequence[ViewProto]: ...
    def add_views(self, view: ViewProto) -> None: ...
    def notify_views(self) -> None: ...


class ControllerProto(Protocol):
    @property
    def view(self) -> ViewProto: ...
    @property
    def model(self) -> ModelProto: ...


VT = TypeVar("VT", bound=ViewProto)
MT = TypeVar("MT", bound=ModelProto)
CT = TypeVar("CT", bound=ControllerProto)

# ------------------------------------------------------------
# Concrete generic classes you will subclass
# We keep them generic, but we don't use parameterized bounds on TypeVars.
# ------------------------------------------------------------


class View(ABC, Frame, Generic[CT, MT]):
    def __init__(self, root: Tk, model: MT) -> None:
        super().__init__(master=root)
        self.__controller: CT  # set later via the property
        self.__model: MT = model
        model.add_views(self)

    @property
    def controller(self) -> CT:
        return self.__controller

    @controller.setter
    def controller(self, controller: CT) -> None:
        self.__controller = controller

    @property
    def model(self) -> MT:
        return self.__model

    @model.setter
    def model(self, model: MT) -> None:
        self.model = model
        model.add_views(self)

    @abstractmethod
    def create_ui(self) -> None: ...

    @abstractmethod
    def refresh(self) -> None: ...


class Model(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.__views: list[ViewProto] = []

    @property
    def views(self) -> Sequence[ViewProto]:
        return self.__views

    def add_views(self, view: ViewProto) -> None:
        self.__views.append(view)

    def notify_views(self) -> None:
        for view in self.__views:
            view.refresh()


class Controller(ABC, Generic[VT, MT]):
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
