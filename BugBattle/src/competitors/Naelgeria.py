"""
Template for a strictly structured Bug.
Main class is abstract,
Has Colony Type Classes, Hunter Type Classes, and the initial set-up class, and Hive setter.
Each Non-abstract class must have it's own Propagator Class

version 1.0
2024-11-21

Python implementation: Phineas Gaucher
"""

from abc import ABC, abstractmethod
from enum import Enum, auto

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


class RoyalDecrees:
    def __init__(self, direction: Direction):
        self.duration = 1
        self.step = 0
        self.current_direction = direction

    def read_decree(self):
        return self.current_direction

    def executed_decree(self):
        self.step += 1
        if self.step == self.duration:
            self.step = 0
            self.duration += 2
            self.current_direction = self.right(self.right(self.current_direction))

    @staticmethod
    def right(direction: Direction):
        transform = {
            Direction.N: Direction.NE,
            Direction.NE: Direction.E,
            Direction.E: Direction.SE,
            Direction.SE: Direction.S,
            Direction.S: Direction.SW,
            Direction.SW: Direction.W,
            Direction.W: Direction.NW,
            Direction.NW: Direction.N,
        }

        return transform[direction]

    @staticmethod
    def left(direction: Direction):
        directions_map_left = {
            Direction.N: Direction.NW,
            Direction.NW: Direction.W,
            Direction.W: Direction.SW,
            Direction.SW: Direction.S,
            Direction.S: Direction.SE,
            Direction.SE: Direction.E,
            Direction.E: Direction.NE,
            Direction.NE: Direction.N,
        }
        return directions_map_left[direction]


class KingdomStage(ABC):
    def __init__(self, bug, direction):
        self.bug = bug  # The object being controlled by the state machine
        self.direction = direction

    @abstractmethod
    def do_action(self):
        pass


class Duke(KingdomStage):
    def __init__(self, bug, direction: [Direction]):
        super().__init__(bug, direction)
        self.has_travelled = False
        self.vertical_complete = False
        self.horizontal_complete = False

    def do_action(self):
        """
        - If `bug.direction` includes 2 cardinalities, spawn Duke in both directions.
        - If only 1 direction, spawn Duke in that direction.
        - Spawn 2 Knights: one North (N) and one South (S).
        - Evolve into Steward(N, S).
        """
        energy = self.bug.get_energy()

        if len(self.direction) == 1 and not self.has_travelled:
            if energy > 2000:
                met_itself = self.bug.move_bug(self.direction[0], fast=True)
                if met_itself:
                    self.bug.suicide()
                self.has_travelled = True
        else:
            self.has_travelled = True

        # This prevents the bug from finish lower_priority_task

        # Start with horizontal growth
        energy = self.bug.get_energy()
        if self.has_travelled and not self.horizontal_complete:
            self.horizontal_complete = True
            for direction in self.direction:
                if self.bug.is_empty(direction):
                    if energy > 1500:
                        self.bug.have_baby(
                            Duke, energy // 2 - 110, [direction], placement=direction
                        )  # Spawn Duke in the direction
                    self.horizontal_complete = True

        # Vertical growth
        energy = self.bug.get_energy()
        if self.horizontal_complete:
            if energy > 2500:
                self.vertical_complete = True
                d = Direction.N
                for direction in [d, d.opposite()]:
                    if self.bug.is_empty(direction):
                        self.bug.have_baby(
                            Knight, energy // 2 - 120, [direction], direction
                        )
            else:
                self.vertical_complete = False

        # Will only be true if both conditions above were met.
        if self.vertical_complete:
            self.bug.change_state(Steward(self.bug, [Direction.W, Direction.E]))


class Knight(KingdomStage):
    def __init__(self, bug, direction):
        super().__init__(bug, direction)
        self.travel_count = 0  # Track how many squares the Knight has traveled
        self.has_travelled = False

    def do_action(self):
        self.travel_count += 1
        """
        - Travel 10 squares in `bug.direction`.
        - Spawn 1 Lord after reaching the destination.
        - After traveling 5 times, evolve into Steward(E, W).
        """

        energy = self.bug.get_energy()

        # If bug has enough energy, move 10 squares
        if energy > 2000 and self.has_travelled == False:
            met_itself = self.bug.move_bug(self.direction[0], fast=True)
            if met_itself:
                self.bug.suicide()
            self.has_travelled = True

        energy = self.bug.get_energy()
        if energy > 2000 and self.has_travelled == True:
            self.bug.have_baby(
                Steward, 1030, [Direction.E, Direction.W], Direction.SE
            )  # Spawn Lord in the same direction
            self.has_travelled = False
            # self.bug.change_state(Steward(self.bug, [Direction.E, Direction.W]))


class Steward(KingdomStage):
    def __init__(self, bug, direction):
        super().__init__(bug, direction)
        self.duke_has_moved = False
        self.horizontal_complete = False
        self.vertical_complete = False

    def do_action(self):
        if len(self.direction) == 2 and not self.duke_has_moved:
            for d in self.direction:
                if not self.bug.is_empty(d):
                    return  # Wait until neighbouring Duke has left.
            self.duke_has_moved = True

        # This prevents the bug from finish lower_priority_task

        # Start with horizontal growth
        energy = self.bug.get_energy()
        if not self.horizontal_complete:
            self.horizontal_complete = (
                True  # Assume true, and change to false if not true
            )
            for d in self.direction:
                if self.bug.is_empty(d):
                    if energy > 2000:
                        self.bug.have_baby(
                            Steward, energy // 2 - 120, [d], placement=d
                        )  # Spawn Duke in the direction
                    else:
                        self.horizontal_complete = False

        # Vertical growth
        energy = self.bug.get_energy()
        if self.horizontal_complete:
            dire = Direction.N
            for d in [dire, dire.opposite()]:
                if self.bug.is_empty(d):
                    if energy > 2000:
                        self.bug.have_baby(Peasant, energy - 200, [d], d)
                        energy = self.bug.get_energy()
                    else:
                        self.vertical_complete = False

        # Will only be true if both conditions above were met.
        if self.vertical_complete:
            self.bug.change_state(Donkey(self.bug, [Direction.W, Direction.E]))


class Peasant(KingdomStage):
    def do_action(self):
        # This prevents the bug from finish lower_priority_task
        previous_task_complete = True  # Assume true, and change to false if not true

        # Vertical growth
        energy = self.bug.get_energy()
        for D in self.direction:
            if self.bug.is_empty(D):
                if energy > 2000:
                    self.bug.have_baby(Peasant, energy - 200, [D], D)
                else:
                    previous_task_complete = False

        # Will only be true if both conditions above were met.
        if previous_task_complete:
            self.bug.change_state(Donkey(self.bug, []))

        pass


class Donkey(KingdomStage):
    def do_action(self):
        class CT(Enum):
            EMPTY, FRIEND, OPPONENT = auto(), auto(), auto()

        for D in Direction:
            creature_type = self.bug.sensor.sense(D)
            if creature_type == Soil or creature_type == Plant:
                creature = CT.EMPTY
            elif creature_type == type(self.bug):
                creature = CT.FRIEND

            else:
                creature = CT.OPPONENT

            match creature:
                case CT.OPPONENT:
                    self.bug.attack(D)
                case CT.EMPTY:
                    if self.bug.get_energy() > 2500:
                        self.bug.have_baby(Donkey, self.bug.get_energy() - 2100, [D], D)
                case CT.FRIEND:  # Don't help friends yet
                    pass

        if self.bug.get_energy() > 2300:
            self.bug.share_food()

        # print("Donkey has no further actions.")
        pass


class BlackPlague(KingdomStage):
    def __init__(self, bug, direction):
        super().__init__(bug, direction)
        decree_direction = direction[0]
        self.orders = RoyalDecrees(decree_direction)

    def do_action(self):
        while self.orders.duration < 95 and self.bug.get_energy() > 5000:
            decree = self.orders.read_decree()
            self.bug.clear(RoyalDecrees.left(decree))
            self.bug.clear(RoyalDecrees.right(decree))
            self.bug.weaken(decree)
            # self.bug.move_bug(decree, False)
            self.orders.executed_decree()
        pass


class RoyalOffspring(Propagator):
    def __init__(self, creature):
        super().__init__(creature)
        self.stage = Peasant
        self.direction = Direction.random()

    def make_child(self):
        child = Naegleria()
        child.evolution = self.stage(child, self.direction)
        return child


class Naegleria(Creature):
    # region instance counting and destroyed
    __instance_count = 0
    __original_bug = None  # Use double underscore for name mangling

    @classmethod
    def instance_count(cls):
        return Naegleria.__instance_count

    @classmethod
    def get_original_bug(cls):
        return Naegleria.__original_bug

    @classmethod
    def set_original_bug(cls, bug):
        Naegleria.__original_bug = bug

    def destroyed(self):
        Naegleria.__instance_count -= 1
        if Naegleria.__original_bug == self:
            Naegleria.__original_bug = None

    # endregion Instance

    def __init__(self, stage=None):
        # region boilerplate
        super().__init__()
        Naegleria.__instance_count += 1

        # Initialize original_bug only if it's None and this is the first instance
        if Naegleria.__original_bug is None:
            Naegleria.__original_bug = self
            self.turn = 0
        # endregion boilerplate

        self.evolution: KingdomStage = (
            stage if stage else Duke(self, [Direction.E, Direction.W])
        )

        # Set-up class values
        self.num_organs = 0
        self.wife = None  # Propagator
        self.chariots = []
        self.sensor = None
        self.energy_sensor = None
        self.poison_sensor = None
        self.poison_gland = None

    def do_turn(self):
        original_bug = Naegleria.get_original_bug()
        if original_bug is not None:
            if original_bug == self:
                self.turn += 1
                if self.turn > 30 and (self.turn + 5) % 10 == 0:
                    self.have_baby(
                        BlackPlague, self.strength() - 200, [Direction.E], Direction.N
                    )
                pass

        if not self.wife:
            self.grow_organs()
        else:
            self.do_action()
        pass

    def grow_organs(self):
        while self.num_organs < 10 and self.strength() > PhotoGland.CREATION_COST + 150:
            PhotoGland(self)
            self.num_organs += 1
        if (
            self.num_organs == 10
            and not self.sensor
            and self.strength() > CreatureTypeSensor.CREATION_COST + 150
        ):
            self.sensor = CreatureTypeSensor(self)
            # self.sensor_energy = EnergySensor(self)
        if (
            self.sensor
            and not self.wife
            and self.strength() > Propagator.CREATION_COST * 2 + 150
        ):
            self.wife = RoyalOffspring(self)  # , self.allowable_dir)
            # self.servant_girl = IllegitimateOffspringMale(self)
        # for i in range(10):
        #     self.chariots.append(Cilia(self))

    def change_state(self, stage):
        self.evolution = stage

    def do_action(self):
        self.evolution.do_action()

    def get_energy(self):
        return self.strength()

    def move_bug(self, direction: Direction, fast) -> bool:
        for i in range(fast * 7 + 1):
            if self.is_empty(direction):
                cilia = Cilia(self)
                cilia.move_in_direction(bearing=direction)
            else:
                return True
        return False

    def suicide(self):
        while self.strength() > 0:
            PoisonGland(self)

    # Direction can be Direction.D, with D being N, NE, E, SE, ...
    def have_baby(
        self,
        type: type[KingdomStage],
        donation: int,
        direction: [Direction],
        placement: Direction,
    ):
        self.wife.stage = type
        self.wife.direction = direction
        self.wife.give_birth(donation, placement)

    def attack(self, direction: Direction):
        # Set up sensors if not yet done
        if self.energy_sensor is None:
            self.energy_sensor = EnergySensor(self)
        if self.poison_sensor is None:
            self.poison_sensor = PoisonSensor(self)

        # Obtain deciding info
        enemy_energy = self.energy_sensor.sense(direction)
        appears_poisonous = self.poison_sensor.sense(direction)

        too_strong = self.strength() < enemy_energy + 150
        if too_strong or appears_poisonous:
            if self.poison_gland is None:
                if (
                    self.strength()
                    > PoisonGland.CREATION_COST + enemy_energy // 4 + 100
                ):
                    self.poison_gland = PoisonGland(self)
            if self.poison_gland:  # I have the tools required, if no poison gland, just hope a neighbour can deal with the threat
                if (
                    self.strength() > enemy_energy // 4 + 100
                ):  # I can kill it with poison
                    if appears_poisonous:  # Kill entirely using poison
                        while True:
                            volume_to_drop = max(
                                0,
                                min(1000, enemy_energy // 4 + 1, self.strength() - 150),
                            )
                            self.poison_gland.add_poison(volume_to_drop)
                            self.poison_gland.drop_poison(direction, volume_to_drop)
                            if volume_to_drop != 1000:
                                break
                            else:
                                enemy_energy = self.energy_sensor.sense(direction)
                        if (
                            self.energy_sensor.sense(direction) <= 0
                            and self.strength() > 400
                        ):
                            self.have_baby(
                                Donkey, self.strength() - 1, [direction], direction
                            )
                    if (
                        too_strong
                    ):  # Reduce enemies health until we are stronger than it
                        # poison_needed_to_kill = (self.strength() + enemy_energy -150) // 5
                        # if poison_needed_to_kill < self.strength():

                        while True:
                            volume_to_drop = min(
                                1000,
                                (enemy_energy - self.strength() + 150) // 3,
                                self.strength() - 10,
                            )
                            self.poison_gland.add_poison(volume_to_drop)
                            self.poison_gland.drop_poison(direction, volume_to_drop)
                            if volume_to_drop != 1000:
                                break
                            else:
                                enemy_energy = self.energy_sensor.sense(direction)
                        if self.strength() > 150:
                            self.have_baby(
                                Donkey, enemy_energy + 1, [direction], direction
                            )
                else:  # I'm not strong enough to kill the enemy myself. So I'll damage it for all I got
                    while True:
                        volume_to_drop = min(1000, self.strength())
                        self.poison_gland.add_poison(volume_to_drop)
                        self.poison_gland.drop_poison(direction, volume_to_drop)
                        if volume_to_drop != 1000:
                            break
                        else:
                            enemy_energy = self.energy_sensor.sense(direction)
            # No poison gland, can't attack enemy
        else:
            self.have_baby(Donkey, enemy_energy + 1, [direction], direction)

    def clear(self, direction: Direction):
        # Set up sensors if not yet done
        if self.sensor is None:
            self.sensor = CreatureTypeSensor(self)
        if self.energy_sensor is None:
            self.energy_sensor = EnergySensor(self)
        if self.poison_sensor is None:
            self.poison_sensor = PoisonSensor(self)
        if self.poison_gland is None:
            self.poison_gland = PoisonGland(self)

        zone_to_clear = self.sensor.sense(direction)
        # We only want to clear out enemies, not plants or friendlies
        if (
            zone_to_clear == Naegleria
            or zone_to_clear == Plant
            or zone_to_clear == Soil
        ):
            return

        # Obtain deciding info
        enemy_energy = self.energy_sensor.sense(direction)
        appears_poisonous = self.poison_sensor.sense(direction)

        if appears_poisonous:  # Kill it
            volume_to_drop = enemy_energy // 4 + 5
            while volume_to_drop > 0:
                payload = min(1000, enemy_energy)
                volume_to_drop -= payload
                self.poison_gland.add_poison(volume_to_drop)
                self.poison_gland.drop_poison(direction, volume_to_drop)
        else:  # eat it and return
            leg = Cilia(self)
            leg.move_in_direction(direction)
            leg = Cilia(self)
            leg.move_in_direction(direction.opposite())

    def weaken(self, direction: Direction):
        # Set up sensors if not yet done
        if self.energy_sensor is None:
            self.energy_sensor = EnergySensor(self)
        if self.poison_sensor is None:
            self.poison_sensor = PoisonSensor(self)
        if self.poison_gland is None:
            self.poison_gland = PoisonGland(self)

        # Obtain deciding info
        enemy_energy = self.energy_sensor.sense(direction)
        appears_poisonous = self.poison_sensor.sense(direction)

        if appears_poisonous:  # Kill it
            volume_to_drop = enemy_energy // 4 + 5
            while volume_to_drop > 0:
                payload = min(1000, enemy_energy)
                volume_to_drop -= payload
                self.poison_gland.add_poison(volume_to_drop)
                self.poison_gland.drop_poison(direction, volume_to_drop)
        elif self.strength() > enemy_energy:  # eat it and return
            pass
        else:
            volume_to_drop = (enemy_energy - self.strength() + 150) // 3
            while volume_to_drop > 0:
                payload = min(1000, enemy_energy)
                volume_to_drop -= payload
                self.poison_gland.add_poison(volume_to_drop)
                self.poison_gland.drop_poison(direction, volume_to_drop)
        cilia = Cilia(self)
        cilia.move_in_direction(bearing=direction)

    def share_food(self):
        if self.energy_sensor is None:
            self.energy_sensor = EnergySensor(self)

        for D in Direction:
            D2 = D.random()
            creature_type = self.sensor.sense(D2)
            if creature_type != type(self):
                return
            friend_energy = self.energy_sensor.sense(D2)
            amount_to_give = min(friend_energy - 1, self.strength() - 2100)
            if amount_to_give > 100:
                self.have_baby(Donkey, amount_to_give, D2, D2)
            if self.strength() <= 2200:
                return
        pass

    def is_empty(self, direction: Direction):
        creature = self.sensor.sense(direction)
        return creature != Naegleria
