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


class SwarmBug(Creature):
    __instance_count = 0

    class Womb(Propagator):
        def make_child(self):
            return Drone()

    def __init__(self):
        super().__init__()
        SwarmBug.__instance_count += 1
        self.womb = None
        self.sensor = None

    @classmethod
    def destroyed(cls):
        SwarmBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return SwarmBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.womb and self.sensor):
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = SwarmBug.Womb(self)
            self._build_if_possible("sensor", CreatureTypeSensor)
            return
        if self.strength() > 400:
            for d in Direction:
                t = self.sensor.sense(d)
                if t in (Soil, Plant):
                    self.womb.give_birth(150, d)


class Drone(SwarmBug):  # helper subclasses main
    def __init__(self):
        super().__init__()

    def do_turn(self):
        pass
