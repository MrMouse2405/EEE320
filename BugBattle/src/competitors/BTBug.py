# ============================================================
# SUPER-NAEGLERIA BEHAVIOR TREE BUG
# ============================================================

import random
from enum import Enum
from typing import List

from shared import (
    Cilia,
    Creature,
    CreatureTypeSensor,
    Direction,
    EnergySensor,
    PhotoGland,
    Plant,
    PoisonGland,
    Propagator,
    Soil,
)

# ------------------------------------------------------------
# BASIC BEHAVIOR TREE NODES
# ------------------------------------------------------------


class Status(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class Node:
    def tick(self, bug):
        raise NotImplementedError


class Selector(Node):
    def __init__(self, *children: Node):
        self.children = children

    def tick(self, bug):
        for c in self.children:
            s = c.tick(bug)
            if s != Status.FAILURE:
                return s
        return Status.FAILURE


class Sequence(Node):
    def __init__(self, *children: Node):
        self.children = children

    def tick(self, bug):
        for c in self.children:
            s = c.tick(bug)
            if s != Status.SUCCESS:
                return s
        return Status.SUCCESS


class Condition(Node):
    def __init__(self, fn):
        self.fn = fn

    def tick(self, bug):
        return Status.SUCCESS if self.fn(bug) else Status.FAILURE


class Action(Node):
    def __init__(self, fn):
        self.fn = fn

    def tick(self, bug):
        self.fn(bug)
        return Status.SUCCESS


# ============================================================
# SUPER-NAEGLERIA BUG
# ============================================================


class Santabarnak(Creature):
    """
    Extremely aggressive, ultra-simple, ultra-fast reproducer.
    This is the strongest possible organism in the BugBattle engine
    aside from genetic-coded Naegleria itself.
    """

    colour = "#00ffaa"
    __instance_count = 0

    MAX_PHOTOS = 6
    MAX_CILIA = 3

    def __init__(self):
        super().__init__()
        Santabarnak.__instance_count += 1

        # ORGANS
        self.photos = 0
        self.cilia: List[Cilia] = []
        self.type_sensor = None
        self.energy_sensor = None
        self.womb = None

        # TARGETS
        self.target_dir = None

        # Full behavior tree
        self.bt = self.build_tree()

    @classmethod
    def instance_count(cls):
        return cls.__instance_count

    @classmethod
    def destroyed(cls):
        cls.__instance_count -= 1

    # ----------------------------------------------------------
    # BEHAVIOR TREE BUILDING
    # ----------------------------------------------------------

    def build_tree(self):
        return Selector(
            # 1. Emergency flee from big threats
            Sequence(
                Condition(lambda b: b.energy_sensor and b.detect_strong_enemy()),
                Action(lambda b: b.flee_enemy()),
            ),
            # 2. Grow essential organs ASAP
            Sequence(
                Condition(lambda b: b.needs_organ_growth()),
                Action(lambda b: b.grow_organs_fast()),
            ),
            # 3. If enough energy → REPRODUCE (main strategy)
            Sequence(
                Condition(lambda b: b.can_reproduce()),
                Action(lambda b: b.reproduce_aggressively()),
            ),
            # 4. Eat plant if next to one
            Sequence(
                Condition(lambda b: b.detect_adjacent_plant()),
                Action(lambda b: b.move_to_target()),
            ),
            # 5. Move into empty space to expand territory
            Sequence(
                Condition(lambda b: b.find_empty_space()),
                Action(lambda b: b.move_to_target()),
            ),
            # 6. Attack small things
            Sequence(
                Condition(lambda b: b.detect_weak_enemy()),
                Action(lambda b: b.move_to_target()),
            ),
            # 7. Fallback random walk
            Action(lambda b: b.random_walk()),
        )

    # ----------------------------------------------------------
    # CONDITIONS
    # ----------------------------------------------------------

    def needs_organ_growth(self):
        """Grow in this order: photos → cilia → type sensor → energy sensor → womb"""
        if self.count_organs() >= 12:
            return False

        if self.photos < Santabarnak.MAX_PHOTOS:
            return self.strength() > PhotoGland.CREATION_COST + 20

        if len(self.cilia) < Santabarnak.MAX_CILIA:
            return self.strength() > Cilia.CREATION_COST + 20

        if (
            self.type_sensor is None
            and self.strength() > CreatureTypeSensor.CREATION_COST + 30
        ):
            return True

        if (
            self.energy_sensor is None
            and self.strength() > EnergySensor.CREATION_COST + 30
        ):
            return True

        if self.womb is None and self.strength() > Propagator.CREATION_COST + 40:
            return True

        return False

    def can_reproduce(self):
        return self.womb is not None and self.strength() > 900

    def detect_adjacent_plant(self):
        if not self.type_sensor:
            return False
        for d in Direction:
            if self.type_sensor.sense(d) == Plant:
                self.target_dir = d
                return True
        return False

    def find_empty_space(self):
        if not self.type_sensor:
            return False
        for d in Direction:
            if self.type_sensor.sense(d) == Soil:
                self.target_dir = d
                return True
        return False

    def detect_weak_enemy(self):
        if not self.type_sensor or not self.energy_sensor:
            return False
        my_str = self.strength()
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, Santabarnak, None):
                if self.energy_sensor.sense(d) < my_str:
                    self.target_dir = d
                    return True
        return False

    def detect_strong_enemy(self):
        if not self.type_sensor or not self.energy_sensor:
            return False
        my_str = self.strength()
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, Santabarnak, None):
                if self.energy_sensor.sense(d) * 1.2 > my_str:
                    self.target_dir = d
                    return True
        return False

    # ----------------------------------------------------------
    # ACTIONS
    # ----------------------------------------------------------

    def grow_organs_fast(self):
        """Grow photoglands → cilia → sensors → womb"""
        if (
            self.photos < Santabarnak.MAX_PHOTOS
            and self.strength() > PhotoGland.CREATION_COST + 20
        ):
            PhotoGland(self)
            self.photos += 1
            return

        if (
            len(self.cilia) < Santabarnak.MAX_CILIA
            and self.strength() > Cilia.CREATION_COST + 20
        ):
            self.cilia.append(Cilia(self))
            return

        if (
            self.type_sensor is None
            and self.strength() > CreatureTypeSensor.CREATION_COST + 30
        ):
            self.type_sensor = CreatureTypeSensor(self)
            return

        if (
            self.energy_sensor is None
            and self.strength() > EnergySensor.CREATION_COST + 30
        ):
            self.energy_sensor = EnergySensor(self)
            return

        if self.womb is None and self.strength() > Propagator.CREATION_COST + 40:
            self.womb = SantabarnakPropagator(self)
            return

    def reproduce_aggressively(self):
        """Produce powerful children with 700–1000 energy."""
        if self.womb and self.strength() > 900:
            give = min(700, self.strength() - 300)
            for d in Direction:
                if self.type_sensor and self.type_sensor.sense(d) == Soil:
                    self.womb.give_birth(give, d)
                    return

    def move_to_target(self):
        if not self.target_dir:
            return
        for c in self.cilia:
            if c.f_uses_this_turn() == 0:
                c.move_in_direction(self.target_dir)
                return

    def flee_enemy(self):
        if not self.target_dir:
            return
        flee_dir = self.target_dir.opposite()
        for c in self.cilia:
            if c.f_uses_this_turn() == 0:
                c.move_in_direction(flee_dir)
                return

    def random_walk(self):
        d = random.choice(list(Direction))
        for c in self.cilia:
            if c.f_uses_this_turn() == 0:
                c.move_in_direction(d)
                return

    # ----------------------------------------------------------
    # CORE TURN LOOP
    # ----------------------------------------------------------

    def do_turn(self):
        self.target_dir = None
        self.bt.tick(self)

    def count_organs(self):
        count = self.photos + len(self.cilia)
        if self.type_sensor:
            count += 1
        if self.energy_sensor:
            count += 1
        if self.womb:
            count += 1
        return count


# ============================================================
# PROPAGATOR
# ============================================================


class SantabarnakPropagator(Propagator):
    def make_child(self):
        return Santabarnak()
