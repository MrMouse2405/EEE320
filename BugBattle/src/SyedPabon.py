# ============================================================
# WhoLetTheBuggOut.py
#
# Authors: OCdt Syed, OCdt Pabon
#
# A Behavior Tree implementation
#
# ============================================================

import random
from enum import Enum, auto
from typing import List, Optional

from shared import (
    Cilia,
    Creature,
    CreatureTypeSensor,
    Direction,
    EnergySensor,
    PhotoGland,
    Plant,
    PoisonGland,
    PoisonSensor,
    Propagator,
    Soil,
)

# ============================================================
# BEHAVIOR TREE FRAMEWORK
# ============================================================


class Status(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3


class Node:
    def tick(self, bug):
        raise NotImplementedError


class Selector(Node):
    def __init__(self, *children):
        self.children = children

    def tick(self, bug):
        for c in self.children:
            r = c.tick(bug)
            if r != Status.FAILURE:
                return r
        return Status.FAILURE


class Sequence(Node):
    def __init__(self, *children):
        self.children = children

    def tick(self, bug):
        for c in self.children:
            r = c.tick(bug)
            if r != Status.SUCCESS:
                return r
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
        return self.fn(bug)


# ============================================================
# ROLES (BEHAVIORAL STATES)
# ============================================================


class Role(Enum):
    HORIZONTAL_EXPANDER = auto()  # Duke: Speed is life. No defense.
    VERTICAL_SCOUT = auto()  # Knight: Long jump. No defense.
    CLUSTER_MANAGER = auto()  # Steward: Local fill.
    VERTICAL_FILLER = auto()  # Peasant: Gap fill.
    HARVESTER = auto()  # Donkey: Aggressive defense & farming.


# ============================================================
# CREATURE IMPLEMENTATION
# ============================================================


class WhoLetTheBuggOut(Creature):
    colour = "#FF0000"  # Aggressive Red
    __instance_count = 0

    MAX_PHOTOS = 10

    def __init__(self):
        super().__init__()
        WhoLetTheBuggOut.__instance_count += 1

        # Organs
        self.num_photos = 0
        self.sensor: Optional[CreatureTypeSensor] = None
        self.energy_sensor: Optional[EnergySensor] = None
        self.poison_sensor: Optional[PoisonSensor] = None
        self.poison_gland: Optional[PoisonGland] = None
        self.womb: Optional["ConfigurablePropagator"] = None

        # State / Memory
        self.role = Role.HORIZONTAL_EXPANDER
        self.assigned_directions: List[Direction] = [Direction.E, Direction.W]

        # Progression Flags
        self.has_travelled = False
        self.horizontal_complete = False
        self.vertical_complete = False

        # Build the Brain
        self.bt = self.build_tree()

    @classmethod
    def instance_count(cls):
        return cls.__instance_count

    @classmethod
    def destroyed(cls):
        cls.__instance_count -= 1

    def do_turn(self):
        self.bt.tick(self)

    # ============================================================
    # BEHAVIOR TREE CONSTRUCTION
    # ============================================================

    def build_tree(self):
        return Selector(
            # 1. CRITICAL SURVIVAL: Grow Organs
            # We strictly prioritize organs to ensure we can execute the strategy.
            Sequence(
                Condition(lambda b: b.needs_organs()),
                Action(lambda b: b.grow_organs_action()),
            ),
            # 2. ROLE EXECUTION (High Priority)
            # We DO NOT check for threats here.
            Sequence(
                Condition(lambda b: b.role == Role.HORIZONTAL_EXPANDER),
                Action(lambda b: b.behavior_horizontal_expansion()),
            ),
            Sequence(
                Condition(lambda b: b.role == Role.VERTICAL_SCOUT),
                Action(lambda b: b.behavior_vertical_scouting()),
            ),
            Sequence(
                Condition(lambda b: b.role == Role.CLUSTER_MANAGER),
                Action(lambda b: b.behavior_cluster_management()),
            ),
            Sequence(
                Condition(lambda b: b.role == Role.VERTICAL_FILLER),
                Action(lambda b: b.behavior_vertical_filling()),
            ),
            # 3. HARVESTER (The "Donkey" phase handles the fighting)
            Sequence(
                Condition(lambda b: b.role == Role.HARVESTER),
                Action(lambda b: b.behavior_harvesting()),
            ),
        )

    # ============================================================
    # 1. ORGAN GROWTH
    # ============================================================

    def needs_organs(self):
        if self.num_photos < self.MAX_PHOTOS:
            return self.strength() > PhotoGland.CREATION_COST + 150
        if not self.sensor:
            return self.strength() > CreatureTypeSensor.CREATION_COST + 150
        if not self.womb:
            return self.strength() > Propagator.CREATION_COST * 2 + 150
        return False

    def grow_organs_action(self):
        if self.num_photos < self.MAX_PHOTOS:
            PhotoGland(self)
            self.num_photos += 1
            return Status.SUCCESS
        if not self.sensor:
            self.sensor = CreatureTypeSensor(self)
            return Status.SUCCESS
        if not self.womb:
            self.womb = ConfigurablePropagator(self)
            return Status.SUCCESS
        return Status.FAILURE

    # ============================================================
    # 2. HELPERS
    # ============================================================

    def have_baby(
        self,
        role: Role,
        donation: int,
        directions: List[Direction],
        placement: Direction,
    ):
        if not self.womb:
            return
        self.womb.configure(role, directions)
        self.womb.give_birth(donation, placement)

    def move_bug(self, direction: Direction):
        """
        Aggressive Movement:
        It does NOT check 'if self.sensor.sense(d) == Soil' inside the loop.
        It blindly fires Cilia. This wastes energy if blocked, but ensures
        maximum speed if clear.
        """
        if self.sensor:
            for _ in range(7):
                # Check if we are blocked by non-soil to stop early (efficiency optimization over original)
                # But primarily we just push.
                target = self.sensor.sense(direction)
                if target == Soil:
                    Cilia(self).move_in_direction(direction)
                else:
                    return  # Blocked

    def attack_target(self, d: Direction):
        """
        Aggressive Combat Logic.
        """
        if not self.energy_sensor:
            self.energy_sensor = EnergySensor(self)
        if not self.poison_sensor:
            self.poison_sensor = PoisonSensor(self)

        enemy_energy = self.energy_sensor.sense(d)
        appears_poisonous = self.poison_sensor.sense(d)

        # If we can't see energy, we can't fight effectively.
        if enemy_energy is None:
            return

        # 1. Do we need poison? (Enemy strong or poisonous)
        if self.strength() < enemy_energy + 150 or appears_poisonous:
            if not self.poison_gland:
                if (
                    self.strength()
                    > PoisonGland.CREATION_COST + enemy_energy // 4 + 100
                ):
                    self.poison_gland = PoisonGland(self)

            if self.poison_gland:
                # DUMP POISON
                while True:
                    # Dump until 1000 or calculated lethal dose
                    dose = min(
                        1000,
                        (enemy_energy - self.strength() + 150) // 3,
                        self.strength() - 10,
                    )
                    if appears_poisonous:
                        dose = max(
                            0, min(1000, enemy_energy // 4 + 1, self.strength() - 150)
                        )

                    if dose <= 0:
                        break

                    self.poison_gland.add_poison(dose)
                    self.poison_gland.drop_poison(d, dose)

                    if dose >= 1000:  # Cap hit, check again next tick
                        break

                    # Re-sense to see if it's dead
                    new_energy = self.energy_sensor.sense(d)
                    if new_energy is None or new_energy <= 0:
                        break
                    enemy_energy = new_energy

        # 2. Spawn Donkey on top (The "Crush" move)
        # If we weakened it enough, or if it was weak to begin with
        current_enemy_energy = self.energy_sensor.sense(d)
        if current_enemy_energy is not None:
            if self.strength() > current_enemy_energy + 50:
                self.have_baby(Role.HARVESTER, current_enemy_energy + 1, [d], d)

    # ============================================================
    # 3. BEHAVIORAL LOGIC (ROLES)
    # ============================================================

    def behavior_horizontal_expansion(self):
        """Matches 'Duke': Move fast E/W, ignore enemies."""
        energy = self.strength()

        # Phase 1: Travel (The "Artery" creation)
        if len(self.assigned_directions) == 1 and not self.has_travelled:
            if energy > 2000:
                self.move_bug(self.assigned_directions[0])  # FAST MOVE
                self.has_travelled = True
        else:
            self.has_travelled = True

        # Phase 2: Spawn more Expanders
        if self.has_travelled and not self.horizontal_complete and self.sensor:
            self.horizontal_complete = True
            for d in self.assigned_directions:
                if self.sensor.sense(d) == Soil:
                    if energy > 1500:
                        self.have_baby(
                            Role.HORIZONTAL_EXPANDER, energy // 2 - 110, [d], d
                        )
                        energy = self.strength()
                    else:
                        self.horizontal_complete = False

        # Phase 3: Vertical Spawn (Scouts)
        if self.horizontal_complete and self.sensor:
            if energy > 2500:
                self.vertical_complete = True
                for d in [Direction.N, Direction.N.opposite()]:
                    if self.sensor.sense(d) == Soil:
                        self.have_baby(Role.VERTICAL_SCOUT, energy // 2 - 120, [d], d)
                        energy = self.strength()
            else:
                self.vertical_complete = False

        if self.vertical_complete:
            self.role = Role.CLUSTER_MANAGER
            self.assigned_directions = [Direction.W, Direction.E]

        return Status.SUCCESS

    def behavior_vertical_scouting(self):
        """Matches 'Knight': Long jump N/S, establish base."""
        energy = self.strength()

        if energy > 2000 and not self.has_travelled:
            self.move_bug(self.assigned_directions[0])  # Jump 1 (7 steps)
            if self.strength() > 1000:
                self.move_bug(self.assigned_directions[0])  # Jump 2 (Ensure distance)
            self.has_travelled = True

        if self.has_travelled and energy > 2000:
            self.have_baby(
                Role.CLUSTER_MANAGER, 1030, [Direction.E, Direction.W], Direction.SE
            )
            self.role = Role.HARVESTER

        return Status.SUCCESS

    def behavior_cluster_management(self):
        """Matches 'Steward': Fill horizontal gaps, spawn Fillers."""
        energy = self.strength()

        if not self.horizontal_complete:
            self.horizontal_complete = True
            if self.sensor:
                for d in self.assigned_directions:
                    if self.sensor.sense(d) == Soil:
                        if energy > 2000:
                            self.have_baby(
                                Role.CLUSTER_MANAGER, energy // 2 - 120, [d], d
                            )
                            energy = self.strength()
                        else:
                            self.horizontal_complete = False

        if self.horizontal_complete:
            if self.sensor:
                for d in [Direction.N, Direction.S]:
                    if self.sensor.sense(d) == Soil:
                        if energy > 2000:
                            self.have_baby(Role.VERTICAL_FILLER, energy - 200, [d], d)
                            energy = self.strength()
                        else:
                            self.vertical_complete = False
                            return Status.SUCCESS
                self.vertical_complete = True

        if self.vertical_complete:
            self.role = Role.HARVESTER

        return Status.SUCCESS

    def behavior_vertical_filling(self):
        """Matches 'Peasant': Fill vertical lines."""
        energy = self.strength()
        task_complete = True

        if self.sensor:
            for d in self.assigned_directions:
                if self.sensor.sense(d) == Soil:
                    if energy > 2000:
                        self.have_baby(Role.VERTICAL_FILLER, energy - 200, [d], d)
                        energy = self.strength()
                    else:
                        task_complete = False

            if task_complete:
                self.role = Role.HARVESTER

        return Status.SUCCESS

    def behavior_harvesting(self):
        """
        Matches 'Donkey'.
        Aggressive:
        1. Attack ANY enemy neighbor.
        2. Spawn into empty Soil.
        3. Share food.
        """

        # 1. AGGRESSIVE SWEEP (Attack Neighbors)
        found_enemy = False
        if self.sensor:
            for d in Direction:
                t = self.sensor.sense(d)
                if t not in (None, Soil, Plant, type(self)):
                    self.attack_target(d)
                    found_enemy = True

        # If we fought, we might be tired, but we continue logic if we can.

        # 2. EXPAND (Farming)
        if self.strength() > 2500 and self.sensor:
            for d in Direction:
                if self.sensor.sense(d) == Soil:
                    # Donkey spawns Donkeys (Harvesters)
                    self.have_baby(Role.HARVESTER, self.strength() - 2100, [d], d)
                    return Status.SUCCESS

        # 3. SHARE FOOD
        if self.strength() > 2300 and self.sensor:
            if not self.energy_sensor:
                self.energy_sensor = EnergySensor(self)
            for d in Direction:
                if self.sensor.sense(d) == type(self):
                    friend_energy = self.energy_sensor.sense(d)
                    amount = min(friend_energy - 1, self.strength() - 2100)
                    if amount > 100:
                        self.have_baby(Role.HARVESTER, amount, [d], d)
                    if self.strength() <= 2200:
                        break

        return Status.SUCCESS


# ============================================================
# CUSTOM PROPAGATOR
# ============================================================


class ConfigurablePropagator(Propagator):
    def __init__(self, creature):
        super().__init__(creature)
        self.next_role = Role.HORIZONTAL_EXPANDER
        self.next_directions = []

    def configure(self, role: Role, directions: List[Direction]):
        self.next_role = role
        self.next_directions = directions

    def make_child(self):
        child = WhoLetTheBuggOut()
        child.role = self.next_role
        child.assigned_directions = self.next_directions
        return child
