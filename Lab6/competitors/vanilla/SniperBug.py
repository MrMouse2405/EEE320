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


class SniperBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        SniperBug.__instance_count += 1
        self.cilia = None
        self.energy_sensor = None
        self.type_sensor = None

    @classmethod
    def destroyed(cls):
        SniperBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return SniperBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.energy_sensor and self.type_sensor):
            self._build_if_possible("cilia", Cilia)
            self._build_if_possible("energy_sensor", EnergySensor)
            self._build_if_possible("type_sensor", CreatureTypeSensor)
            return
        best_d = None
        best_e = 10**9
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t is Soil:
                continue
            e = self.energy_sensor.sense(d)
            if e < best_e:
                best_e, best_d = e, d
        self.cilia.move_in_direction(best_d or Direction.random())
