"""
BugBattle Competitor
Fixed pack: 20 archetypes, each in its own file.
- Propagators are concrete (no abstract instantiation).
- Any helper creature subclasses the main class (per shared.py rules).
- No use of framework f_* internals.
"""

from __future__ import annotations

from shared import (
    Cilia,
    Cloaking,
    Creature,
    CreatureTypeSensor,
    Direction,
    EnergySensor,
    LifeSensor,
    PhotoGland,
    Plant,
    PoisonGland,
    PoisonSensor,
    Propagator,
    Soil,
    Spikes,
)


class FarmerBug(Creature):
    __instance_count = 0

    class Seedling(FarmerBug if False else Creature):  # placeholder for type checker
        pass

    class FarmerSeed(FarmerBug):  # helper must subclass main
        def __init__(self):
            super().__init__()
            # keep it simple: give it a leaf and then do nothing
            if self.strength() > PhotoGland.CREATION_COST:
                PhotoGland(self)

        def do_turn(self):
            pass  # seedlings are passive

    class Womb(Propagator):
        def make_child(self):
            return FarmerBug.FarmerSeed()

    def __init__(self):
        super().__init__()
        FarmerBug.__instance_count += 1
        self.cilia = None
        self.type_sensor = None
        self.womb = None
        self.leaf = None

    @classmethod
    def destroyed(cls):
        FarmerBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return FarmerBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.type_sensor and self.womb and self.leaf):
            self._build_if_possible("cilia", Cilia)
            self._build_if_possible("type_sensor", CreatureTypeSensor)
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = FarmerBug.Womb(self)
            if self.leaf is None and self.strength() > PhotoGland.CREATION_COST:
                self.leaf = PhotoGland(self)
            return
        if self.strength() > 0.6 * Creature.MAX_STRENGTH:
            for d in Direction:
                t = self.type_sensor.sense(d)
                if t in (Soil, Plant):
                    self.womb.give_birth(self.strength() / 4, d)
                    break
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, type(self)):
                self.cilia.move_in_direction(d)
                return
        self.cilia.move_in_direction(Direction.random())
