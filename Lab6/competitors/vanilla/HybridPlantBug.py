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

class HybridPlantBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        HybridPlantBug.__instance_count += 1
        self.cilia = None
        self.leaf = None
        self.sensor = None

    @classmethod
    def destroyed(cls):
        HybridPlantBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return HybridPlantBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.leaf and self.sensor):
            self._build_if_possible('leaf', PhotoGland)
            self._build_if_possible('sensor', CreatureTypeSensor)
            self._build_if_possible('cilia', Cilia)
            return
        if self.strength() > 0.7 * Creature.MAX_STRENGTH and self.cilia:
            for d in Direction:
                t = self.sensor.sense(d)
                if t not in (Soil, Plant, type(self)):
                    self.cilia.move_in_direction(d)
                    return
        if self.cilia:
            self.cilia.move_in_direction(Direction.random())
