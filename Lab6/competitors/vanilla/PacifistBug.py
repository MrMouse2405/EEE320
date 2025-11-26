"""
BugBattle Competitor
Fixed pack: 20 archetypes, each in its own file.
- Propagators are concrete (no abstract instantiation).
- Any helper creature subclasses the main class (per shared.py rules).
- No use of framework f_* internals.
"""

from shared import (
    Creature,
    Cilia,
    PhotoGland,
    Propagator,
    Direction,
    Spikes,
    Cloaking,
    EnergySensor,
    CreatureTypeSensor,
    LifeSensor,
    PoisonSensor,
    Plant,
    Soil,
    PoisonGland,
)


class PacifistBug(Creature):
    __instance_count = 0

    class Womb(Propagator):
        def make_child(self):
            return PacifistBug()

    def __init__(self):
        super().__init__()
        PacifistBug.__instance_count += 1
        self.leaf = None
        self.womb = None
        self.sensor = None

    @classmethod
    def destroyed(cls):
        PacifistBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return PacifistBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.leaf and self.womb and self.sensor):
            self._build_if_possible("leaf", PhotoGland)
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = PacifistBug.Womb(self)
            self._build_if_possible("sensor", CreatureTypeSensor)
            return
        if self.strength() > 0.55 * Creature.MAX_STRENGTH:
            for d in Direction:
                t = self.sensor.sense(d)
                if t in (Soil, Plant):
                    self.womb.give_birth(self.strength() / 2.5, d)
                    break
