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

class CloakHunterBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        CloakHunterBug.__instance_count += 1
        self.cilia = None
        self.cloak = None
        self.life_sensor = None

    @classmethod
    def destroyed(cls):
        CloakHunterBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return CloakHunterBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.cloak and self.life_sensor):
            self._build_if_possible('cilia', Cilia)
            self._build_if_possible('cloak', Cloaking)
            self._build_if_possible('life_sensor', LifeSensor)
            return
        adjacent_life = any(self.life_sensor.sense(d) for d in Direction)
        if adjacent_life:
            self.cloak.uncloak()
            for d in Direction:
                if self.life_sensor.sense(d):
                    self.cilia.move_in_direction(d)
                    return
        else:
            self.cloak.cloak()
            self.cilia.move_in_direction(Direction.random())
