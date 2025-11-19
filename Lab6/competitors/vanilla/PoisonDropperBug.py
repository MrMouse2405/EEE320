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

class PoisonDropperBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        PoisonDropperBug.__instance_count += 1
        self.cilia = None
        self.poison = None
        self.type_sensor = None

    @classmethod
    def destroyed(cls):
        PoisonDropperBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return PoisonDropperBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.poison and self.type_sensor):
            self._build_if_possible('cilia', Cilia)
            self._build_if_possible('poison', PoisonGland)
            self._build_if_possible('type_sensor', CreatureTypeSensor)
            return
        enemy_dir = None
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, type(self)):
                enemy_dir = d
                break
        if enemy_dir:
            self.poison.drop_poison(enemy_dir, 50)
            self.cilia.move_in_direction(enemy_dir.opposite())
        else:
            if self.strength() > 0.6 * Creature.MAX_STRENGTH:
                self.poison.drop_poison(Direction.random(), 20)
            self.cilia.move_in_direction(Direction.random())
