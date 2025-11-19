"""
BugBattle Competitor
Fixed pack: 20 archetypes, each in its own file.
- Propagators are concrete (no abstract instantiation).
- Any helper creature subclasses the main class (per shared.py rules).
- No use of framework f_* internals.
"""
from shared import (
    Creature, Cilia, PhotoGland, Propagator, Direction,
    Spikes, Cloaking,
    EnergySensor, CreatureTypeSensor, LifeSensor, PoisonSensor,
    Plant, Soil, PoisonGland
)

class AggressorBug(Creature):
    __instance_count = 0

    class Womb(Propagator):
        def make_child(self):
            return AggressorBug()

    def __init__(self):
        super().__init__()
        AggressorBug.__instance_count += 1
        self.cilia = None
        self.type_sensor = None
        self.womb = None

    @classmethod
    def destroyed(cls):
        AggressorBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return AggressorBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.type_sensor and self.womb):
            self._build_if_possible('cilia', Cilia)
            self._build_if_possible('type_sensor', CreatureTypeSensor)
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = AggressorBug.Womb(self)
            return
        if self.strength() > 0.9 * Creature.MAX_STRENGTH:
            for d in Direction:
                seen = self.type_sensor.sense(d)
                if seen in (Soil, Plant):
                    self.womb.give_birth(self.strength() / 3, d)
                    break
        for d in Direction:
            seen = self.type_sensor.sense(d)
            if seen not in (Soil, type(self)):
                self.cilia.move_in_direction(d)
                return
        self.cilia.move_in_direction(Direction.random())
