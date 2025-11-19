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

class SelfDestructBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        SelfDestructBug.__instance_count += 1
        self.cilia = None
        self.poison = None
        self.type_sensor = None

    @classmethod
    def destroyed(cls):
        SelfDestructBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return SelfDestructBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.poison and self.type_sensor):
            self._build_if_possible('cilia', Cilia)
            self._build_if_possible('poison', PoisonGland)
            self._build_if_possible('type_sensor', CreatureTypeSensor)
            return
        if self.strength() < 300:
            self.poison.drop_poison(Direction.random(), 120)
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, type(self)):
                self.cilia.move_in_direction(d)
                return
        self.cilia.move_in_direction(Direction.random())
