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


class HiveBug(Creature):
    __instance_count = 0

    class Womb(Propagator):
        def make_child(self):
            return Worker()

    def __init__(self):
        super().__init__()
        HiveBug.__instance_count += 1
        self.womb = None
        self.sensor = None
        self.cilia = None

    @classmethod
    def destroyed(cls):
        HiveBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return HiveBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.womb and self.sensor and self.cilia):
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = HiveBug.Womb(self)
            self._build_if_possible("sensor", CreatureTypeSensor)
            self._build_if_possible("cilia", Cilia)
            return
        if self.strength() > 0.6 * Creature.MAX_STRENGTH:
            for d in Direction:
                t = self.sensor.sense(d)
                if t in (Soil, Plant):
                    self.womb.give_birth(self.strength() / 5, d)
                    break
        self.cilia.move_in_direction(Direction.random())


class Worker(HiveBug):  # helper subclasses main
    def __init__(self):
        super().__init__()

    def do_turn(self):
        if (
            hasattr(self, "cilia")
            and self.cilia is None
            and self.strength() > Cilia.CREATION_COST
        ):
            self.cilia = Cilia(self)
        if hasattr(self, "cilia") and self.cilia:
            self.cilia.move_in_direction(Direction.random())
