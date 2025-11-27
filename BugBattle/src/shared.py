from __future__ import annotations

import math
import random
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Self, override

import numpy as np
from numpy.typing import NDArray

"""
This module contains classes which form part of the BugBattle
system and which are used in the creation of competitor creatures.

Competitor creatures are forbidden from accessing private
attributes and methods as well as attributes and methods whose
names start with `f_` or `F_`. These are reserved for game framework
use.

version 1.13 (NumPy optimized)
2021-11-23

Python implementation: Greg Phillips
Based on an original design by Scott Knight and a series of
implementations in C++ and Java by Scott Knight and Greg Phillips
"""

"""

    Direction

"""


class Direction(Enum):
    N = (0, -1)
    NE = (1, -1)
    E = (1, 0)
    SE = (1, 1)
    S = (0, 1)
    SW = (-1, 1)
    W = (-1, 0)
    NW = (-1, -1)

    def __init__(self, dx: int, dy: int) -> None:
        self.dx: int = dx
        self.dy: int = dy

    def opposite(self) -> Direction:
        return Direction((-self.dx, -self.dy))

    @classmethod
    def random(cls) -> Direction:
        return random.choice(list(cls))


"""

    World

"""


class World:
    """
    Looks after the location of all creatures in the World and allows
    each to perform its turn. Empty locations are represented by instances
    of Soil.
    """

    def __init__(self, width: int) -> None:
        self.width: int = width
        # Use object dtype array for creature references
        self.locations: NDArray[np.object_] = np.empty(width * width, dtype=object)
        self._indices = np.arange(width * width, dtype=np.int32)
        self.reset()

    def reset(self) -> None:
        # Vectorized destruction
        if len(self.locations) > 0:
            for location in self.locations:
                if location is not None:
                    location.destroyed()

        self.locations = np.empty(self.width * self.width, dtype=object)
        for index in self._indices:
            self.place(Soil(), index)  # type: ignore

    def place(self, creature: Creature, destination: int) -> None:
        creature.f_set_location(destination)
        self.locations[destination] = creature
        creature.f_set_world(self)

    def replace(self, original: Creature, replacement: Creature) -> None:
        try:
            destination = self.location_of(original)
            self.place(replacement, destination)
        except ValueError:
            pass

    def location_of(self, creature: Creature) -> int:
        loc = creature.f_location()
        if self.locations[loc] == creature:
            return loc
        else:
            raise ValueError()

    def creature_at(self, index: int) -> Creature:
        return self.locations[index]

    def creature_at_offset_from(
        self, creature: Creature, bearing: Direction
    ) -> Creature:
        try:
            start = self.location_of(creature)
            target = self._location_offset(start, bearing)
            return self.creature_at(target)
        except ValueError:
            return Soil()

    def do_turn(self) -> None:
        """
        Executes the metabolic cycle for all creatures then permits each to
        do its turn.

        One subtlety: since creatures can move, if we simply iterated
        over the locations list for do_turn, it's possible that a creature moving
        west or south would get more than one turn in a single world turn (since
        it could have moved into a location whose turn had not yet come up). So,
        we call do_turn over a copy of the locations list.
        """
        # Metabolic cycle for all creatures
        for creature in self.locations:
            creature.f_metabolic_cycle()

        # Copy the array for iteration
        creatures_snapshot = self.locations.copy()
        for ix, creature in enumerate(creatures_snapshot):
            creature.do_turn()
            creature.f_cap_strength()

        # Replace dead creatures
        for creature in self.locations.copy():
            if not creature.is_alive():
                self.replace(creature, Soil())

    def move(self, attacker: Creature, bearing: Direction) -> None:
        """
        If the creature is in the world, attempts to move it by attacking
        the location at the bearing from its initial location, back-filling
        the location it moved out of with a NullCreature.

        A creature might not be in the world if it has already been attacked on this turn
        but is now being permitted to have its turn; see the note on World.do_turn.
        """
        try:
            start = self.location_of(attacker)
        except ValueError:
            return
        self.place(Soil(), start)
        self.launch_attack(start, bearing, attacker)

    def launch_attack(self, start: int, bearing: Direction, attacker: Creature) -> None:
        battleground: int = self._location_offset(start, bearing)
        winner: Creature = attacker.f_attack(self.locations[battleground])
        self.place(winner, battleground)

    def drop_beside(
        self, origin_creature: Creature, dropped: Creature, bearing: Direction
    ) -> None:
        try:
            start = self.location_of(origin_creature)
            self.launch_attack(start, bearing, dropped)
        except ValueError:
            pass

    def _location_offset(self, start: int, bearing: Direction) -> int:
        """Returns the start location offset by bearing, accounting for edge wrapping."""
        new_x = (start % self.width + bearing.dx) % self.width
        new_y = (start // self.width + bearing.dy) % self.width
        return new_y * self.width + new_x


"""

    Creature

"""


class Creature(ABC):
    """
    The abstract superclass of all creatures.

    Subclasses must have a class attribute __instance_count which must be

    - incremented in the subclass constructor
    - decremented in a class method called destroyed()
    - returned from a class method called instance_count()

    If you have multiple Creature subclasses as part of your competitor strategy,
    then a few things are required to make instance counting and colour coding in
    in the view work properly.

    1. All your competitor classes MUST be subclasses of your main competitor class,
    and MUST NOT define their own __instance_count attribute, destroyed() method, or
    instance_count() method.

    2. All accesses MUST use the explicit name of the main competitor class. E.g., if
    your main competitor is Hunter, its destroyed() method must be

        @classmethod
        def destroyed(cls):
            Hunter.__instance_count -= 1

    and NOT

        @classmethod
        def destroyed(cls):
            cls.__instance_count -= 1

    See the Hunter and LittleHunter classes in competitors/HuntingInstructors.py
    for an example.

    """

    __MAX_STRENGTH: int = 2000
    __MAINTENANCE_COST: int = 20
    __MAX_ORGANS: int = 10
    __DEAD_COLOUR: str = "black"

    MAX_STRENGTH = __MAX_STRENGTH
    MAINTENANCE_COST = __MAINTENANCE_COST
    MAX_ORGANS = __MAX_ORGANS
    DEAD_COLOUR = __DEAD_COLOUR

    def __init__(self) -> None:
        self.__world: World | None = None
        self.__location: int | None = None
        self.__alive: bool = True
        self.__strength: int = 0
        self.__colour: str | None = None
        self.__organs: list[Organ] = []
        self.__cloaked: bool = False
        self.__poisonous: bool = False

    @abstractmethod
    def do_turn(self) -> None: ...

    @classmethod
    @abstractmethod
    def destroyed(cls) -> None: ...

    @classmethod
    @abstractmethod
    def instance_count(cls) -> int: ...

    def strength(self) -> int:
        return self.__strength

    def is_alive(self) -> bool:
        return self.__alive

    def f_set_world(self, world: World) -> None:
        self.__world = world

    def f_world(self) -> World:
        return self.__world  # type: ignore

    def f_set_location(self, location: int) -> None:
        self.__location = location

    def f_location(self) -> int:
        return self.__location  # type: ignore

    @staticmethod
    def f_fights_back() -> bool:
        return True

    def f_apparent_strength(self) -> int:
        return 0 if self.__cloaked else self.__strength

    def f_apparent_type(self) -> type[Soil] | type[Self]:
        return Soil if self.__cloaked else type(self)

    def f_appears_poisonous(self) -> bool:
        return self.__poisonous and not self.__cloaked

    def f_add_organ(self, organ: Organ) -> None:
        self.f_expend(organ.creation_cost())
        if len(self.__organs) < self.__MAX_ORGANS:
            self.__organs.append(organ)

    def f_defensive_damage(self) -> int:
        # Use sum() with generator for efficiency
        return sum(organ.f_defensive_damage() for organ in self.__organs)

    def f_metabolic_cycle(self) -> None:
        for organ in self.__organs:
            organ.f_new_turn()
            self.f_expend(organ.maintenance_cost())
        self.f_expend(self.__MAINTENANCE_COST)

    def f_cap_strength(self) -> None:
        self.__strength = min(self.__strength, self.__MAX_STRENGTH)

    def f_feed(self, food_energy: int) -> None:
        if self.__alive:
            self.__strength += food_energy

    def f_expend(self, food_energy: int) -> None:
        self.__strength -= food_energy
        if self.__strength < 0:
            self.f_die()

    def f_die(self) -> None:
        if self.__alive:
            self.destroyed()
        self.__strength = 0
        self.__alive = False

    def f_replace_me_with(self, replacement: Creature) -> None:
        self.__world.replace(self, replacement)  # type: ignore

    def f_attack(self, defender: Creature) -> Self | Creature:
        if not defender.f_fights_back():
            return self.__attacker_wins(defender)
        if not self.f_fights_back():
            return self.__defender_wins(defender)
        if self.__strength > defender.strength():
            return self.__attacker_wins(defender)
        return self.__defender_wins(defender)

    def __defender_wins(self, defender: Creature) -> Creature:
        defender.f_feed(self.__strength - self.f_defensive_damage())
        self.f_die()
        return defender

    def __attacker_wins(self, defender: Creature) -> Self:
        self.f_feed(defender.strength() - defender.f_defensive_damage())
        defender.f_die()
        return self

    def f_cloak(self) -> None:
        self.__cloaked = True

    def f_uncloak(self) -> None:
        self.__cloaked = False

    def f_is_cloaked(self) -> bool:
        return self.__cloaked

    def f_become_poisonous(self) -> None:
        self.__poisonous = True


"""

    Organ

"""


class Organ(ABC):
    F_CREATION_COST: int | None = None
    F_USE_COST: int | None = None
    F_MAINTENANCE_COST: int | None = None

    def __init__(self, host: Creature) -> None:
        self.__host: Creature = host
        host.f_add_organ(self)
        self.__uses_this_turn: int = 0  # currently affects only Cilia

    def host(self) -> Creature:
        return self.__host

    def creation_cost(self) -> int:
        return self.F_CREATION_COST  # type: ignore

    def use_cost(self) -> int:
        return self.F_USE_COST  # type: ignore

    def maintenance_cost(self) -> int:
        return self.F_MAINTENANCE_COST  # type: ignore

    def f_new_turn(self) -> None:
        self.__uses_this_turn = 0

    def f_used_once(self) -> None:
        self.__uses_this_turn += 1

    def f_uses_this_turn(self) -> int:
        return self.__uses_this_turn

    def f_defensive_damage(self) -> int:
        return 0

    def f_host_would_be_alive_after_use(self) -> bool:
        self.host().f_expend(self.use_cost())
        return self.__host.is_alive()


"""

    Soil / Plant / PoisonDrop

"""


class Soil(Creature):
    __PLANT_GROWTH_PROBABILITY: float = 0.01
    __instance_count: int = 0
    colour: str = ""

    def __init__(self) -> None:
        super().__init__()
        Soil.__instance_count += 1

    def do_turn(self) -> None:
        if random.random() < self.__PLANT_GROWTH_PROBABILITY:
            self.become_plant()

    def become_plant(self) -> None:
        self.f_replace_me_with(Plant())

    @classmethod
    def instance_count(cls) -> int:
        return Soil.__instance_count

    @classmethod
    def destroyed(cls) -> None:
        Soil.__instance_count -= 1

    @staticmethod
    def f_fights_back() -> bool:
        return False

    def f_expend(self, food_energy: int) -> None:
        pass

    def f_feed(self, food_energy: int) -> None:
        pass

    def f_die(self) -> None:
        pass


class Plant(Creature):
    __instance_count: int = 0
    colour: str = "#d2f53c"

    def __init__(self) -> None:
        super().__init__()
        Plant.__instance_count += 1
        self.f_feed(PhotoGland.CREATION_COST + Propagator.CREATION_COST)
        PhotoGland(self)
        self.propagator: PlantPropagator = PlantPropagator(self)

    @staticmethod
    def f_fights_back() -> bool:
        return False

    def do_turn(self) -> None:
        if self.strength() > Creature.MAX_STRENGTH:
            self.propagator.give_birth(self.strength() / 2, Direction.random())

    @classmethod
    def instance_count(cls) -> int:
        return Plant.__instance_count

    @classmethod
    def destroyed(cls) -> None:
        Plant.__instance_count -= 1


class PoisonDrop(Creature):
    F_DISSIPATION_RATE: float = 0.5
    __instance_count: int = 0
    colour: str = "black"

    def __init__(self, volume: int) -> None:
        super().__init__()
        self.f_feed(1 + volume)
        self.__gland: PoisonGland = PoisonGland(self)
        self.__gland.add_poison(volume)
        super().f_expend(volume)
        PoisonDrop.__instance_count += 1

    def f_apparent_type(self) -> type[Soil]:
        return Soil

    def f_expend(self, food_energy: int) -> None:
        pass

    def do_turn(self) -> None:
        volume = math.ceil(self.__gland.current_volume() * self.F_DISSIPATION_RATE)
        self.__gland.remove_poison(volume)
        if self.__gland.current_volume() <= 0:
            self.f_die()

    @classmethod
    def instance_count(cls) -> int:
        return PoisonDrop.__instance_count

    @classmethod
    def destroyed(cls) -> None:
        PoisonDrop.__instance_count -= 1


"""

    Organs

"""


class Cilia(Organ):
    F_CREATION_COST = CREATION_COST = 100
    F_MAINTENANCE_COST = MAINTENANCE_COST = 10
    F_USE_COST = USE_COST = 20

    def move_in_direction(self, bearing: Direction) -> None:
        if self.f_host_would_be_alive_after_use() and self.f_uses_this_turn() == 0:
            self.f_used_once()
            self.host().f_world().move(self.host(), bearing)


class PhotoGland(Organ):
    F_CREATION_COST = CREATION_COST = 250
    F_MAINTENANCE_COST = MAINTENANCE_COST = -150


class Propagator(Organ, ABC):
    F_CREATION_COST = CREATION_COST = 50
    F_MAINTENANCE_COST = MAINTENANCE_COST = 5
    F_USE_COST = USE_COST = 100

    def give_birth(self, initial_energy: float, direction: Direction) -> None:
        self.host().f_expend(int(initial_energy))
        if self.f_host_would_be_alive_after_use():
            child = self.make_child()
            child.f_feed(int(initial_energy))
            self.host().f_world().drop_beside(self.host(), child, direction)

    @abstractmethod
    def make_child(self) -> Creature:
        pass


class PlantPropagator(Propagator):
    @override
    def make_child(self) -> Plant:
        return Plant()


class Cloaking(Organ):
    F_CREATION_COST = CREATION_COST = 500
    F_MAINTENANCE_COST = MAINTENANCE_COST = 10
    F_USE_COST = USE_COST = 100

    def cloak(self) -> None:
        if self.f_host_would_be_alive_after_use():
            self.host().f_cloak()

    def uncloak(self) -> None:
        self.host().f_uncloak()

    def maintenance_cost(self) -> int:
        return self.F_MAINTENANCE_COST + (
            self.F_USE_COST if self.host().f_is_cloaked() else 0
        )  # type: ignore


class Sensor(Organ, ABC):
    F_DEFAULT_VALUE: Any = None

    def sense(self, direction: Direction) -> Any:
        if self.f_host_would_be_alive_after_use():
            target = (
                self.host().f_world().creature_at_offset_from(self.host(), direction)
            )
            return self.sensor_value(target)
        else:
            return self.F_DEFAULT_VALUE

    @abstractmethod
    def sensor_value(self, target: Creature) -> Any:
        pass


class EnergySensor(Sensor):
    F_DEFAULT_VALUE: int = 0
    F_CREATION_COST = CREATION_COST = 100
    F_MAINTENANCE_COST = MAINTENANCE_COST = 10
    F_USE_COST = USE_COST = 2

    def sensor_value(self, target: Creature) -> int:
        return target.f_apparent_strength()


class CreatureTypeSensor(Sensor):
    F_DEFAULT_VALUE: type[Soil] = Soil
    F_CREATION_COST = CREATION_COST = 100
    F_MAINTENANCE_COST = MAINTENANCE_COST = 10
    F_USE_COST = USE_COST = 2

    def sensor_value(self, target: Creature) -> type:
        return target.f_apparent_type()


class LifeSensor(Sensor):
    F_DEFAULT_VALUE: bool = False
    F_CREATION_COST = CREATION_COST = 50
    F_MAINTENANCE_COST = MAINTENANCE_COST = 5
    F_USE_COST = USE_COST = 1

    def sensor_value(self, target: Creature) -> bool:
        return target.f_apparent_type() != Soil


class PoisonSensor(Sensor):
    F_DEFAULT_VALUE: bool = False
    F_CREATION_COST = CREATION_COST = 50
    F_MAINTENANCE_COST = MAINTENANCE_COST = 5
    F_USE_COST = USE_COST = 1

    def sensor_value(self, target: Creature) -> bool:
        return target.f_appears_poisonous()


class PoisonGland(Organ):
    F_CREATION_COST = CREATION_COST = 500
    F_MAINTENANCE_COST = MAINTENANCE_COST = 20
    __RESERVOIR_CAPACITY: int = 1000
    __DAMAGE_MULTIPLIER: int = 4

    def __init__(self, host: Creature) -> None:
        super().__init__(host)
        self.host().f_become_poisonous()
        self.__reservoir_volume: int = 0

    def f_defensive_damage(self) -> int:
        return self.__reservoir_volume * self.__DAMAGE_MULTIPLIER

    def add_poison(self, to_add: int) -> None:
        if to_add <= 0:
            return
        to_add = min(self.host().strength(), to_add)
        self.host().f_expend(to_add)
        self.__reservoir_volume = min(
            self.__RESERVOIR_CAPACITY, self.__reservoir_volume + to_add
        )

    def remove_poison(self, to_remove: int) -> None:
        if to_remove > 0:
            self.__reservoir_volume = max(0, self.__reservoir_volume - to_remove)

    def current_volume(self) -> int:
        return self.__reservoir_volume

    def drop_poison(self, direction: Direction, volume_desired: int) -> None:
        if volume_desired <= 0:
            return
        volume = min(self.__reservoir_volume, volume_desired)
        self.__reservoir_volume -= volume
        drop = PoisonDrop(volume)
        self.host().f_world().drop_beside(self.host(), drop, direction)


class Spikes(Organ):
    F_CREATION_COST = CREATION_COST = 100
    F_MAINTENANCE_COST = MAINTENANCE_COST = 5
    F_DEFENSIVE_DAMAGE = DEFENSIVE_DAMAGE = 200

    @override
    def f_defensive_damage(self) -> int:
        return self.F_DEFENSIVE_DAMAGE
