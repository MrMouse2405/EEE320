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

class TankBug(Creature):
    __instance_count = 0

    def __init__(self):
        super().__init__()
        TankBug.__instance_count += 1
        self.cilia = None
        self.spikes = None
        self.leaf = None

    @classmethod
    def destroyed(cls):
        TankBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return TankBug.__instance_count

    def do_turn(self):
        if not (self.spikes and self.leaf):
            if self.spikes is None and self.strength() > Spikes.CREATION_COST:
                self.spikes = Spikes(self)
            if self.leaf is None and self.strength() > PhotoGland.CREATION_COST:
                self.leaf = PhotoGland(self)
            if self.cilia is None and self.strength() > Cilia.CREATION_COST:
                self.cilia = Cilia(self)
            return
        if self.cilia and Direction.random().value[1] == 0:
            self.cilia.move_in_direction(Direction.random())
