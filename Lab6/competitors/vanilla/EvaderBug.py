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


class EvaderBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        EvaderBug.__instance_count += 1
        self.cilia = None
        self.poison_sensor = None
        self.type_sensor = None

    @classmethod
    def destroyed(cls):
        EvaderBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return EvaderBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.poison_sensor and self.type_sensor):
            self._build_if_possible("cilia", Cilia)
            self._build_if_possible("poison_sensor", PoisonSensor)
            self._build_if_possible("type_sensor", CreatureTypeSensor)
            return
        for d in Direction:
            if not self.poison_sensor.sense(d):
                t = self.type_sensor.sense(d)
                if t in (Soil, Plant):
                    self.cilia.move_in_direction(d)
                    return
        self.cilia.move_in_direction(Direction.random())
