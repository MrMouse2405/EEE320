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

class AmbusherBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        AmbusherBug.__instance_count += 1
        self.cilia = None
        self.cloak = None
        self.type_sensor = None

    @classmethod
    def destroyed(cls):
        AmbusherBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return AmbusherBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.cilia and self.cloak and self.type_sensor):
            self._build_if_possible('cilia', Cilia)
            self._build_if_possible('cloak', Cloaking)
            self._build_if_possible('type_sensor', CreatureTypeSensor)
            return
        prey_dir = None
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, type(self)):
                prey_dir = d
                break
        if prey_dir:
            self.cloak.uncloak()
            self.cilia.move_in_direction(prey_dir)
        else:
            self.cloak.cloak()
            if self.cilia:
                self.cilia.move_in_direction(Direction.random())
