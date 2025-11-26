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


class DefenderBug(Creature):
    __instance_count = 0

    class Womb(Propagator):
        def make_child(self):
            return DefenderBug()

    def __init__(self):
        super().__init__()
        DefenderBug.__instance_count += 1
        self.cilia = None
        self.spikes = None
        self.poison = None
        self.womb = None

    @classmethod
    def destroyed(cls):
        DefenderBug.__instance_count -= 1

    @classmethod
    def instance_count(cls):
        return DefenderBug.__instance_count

    def _build_if_possible(self, attr, organ_cls):
        if getattr(self, attr) is None and self.strength() > organ_cls.CREATION_COST:
            setattr(self, attr, organ_cls(self))

    def do_turn(self):
        if not (self.spikes and self.poison and self.womb):
            if self.spikes is None and self.strength() > Spikes.CREATION_COST:
                self.spikes = Spikes(self)
            if self.poison is None and self.strength() > PoisonGland.CREATION_COST:
                self.poison = PoisonGland(self)
            if self.womb is None and self.strength() > Propagator.CREATION_COST:
                self.womb = DefenderBug.Womb(self)
            self._build_if_possible("cilia", Cilia)
            return
        if self.strength() > 0.75 * Creature.MAX_STRENGTH:
            self.poison.drop_poison(Direction.random(), 30)
        if self.cilia and Direction.random().value[0] == 0:
            self.cilia.move_in_direction(Direction.random())
