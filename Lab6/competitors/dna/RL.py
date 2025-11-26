import numpy as np
import random
from shared import (
    Creature,
    Soil,
    Plant,
    Direction,
    Cilia,
    CreatureTypeSensor,
    EnergySensor,
    LifeSensor,
    PoisonSensor,
    PhotoGland,
    Spikes,
    Cloaking,
    Propagator,
    PoisonGland,
)

# ===============================
#   SimpleRLV3 — MAIN CLASS
# ===============================


class SimpleRLV3(Creature):
    __instance_count = 0
    colour = "#44aa99"

    # --------------------------------------------
    # DNA layout (20 parameters, RL-friendly)
    # --------------------------------------------
    DEFAULT_DNA = np.array(
        [
            # A. organ growth thresholds
            100,  # 0 grow_cilia
            150,  # 1 grow_type_sensor
            200,  # 2 grow_energy_sensor
            180,  # 3 grow_life_sensor
            200,  # 4 grow_poison_sensor
            300,  # 5 grow_photogland
            250,  # 6 grow_spikes
            500,  # 7 grow_cloak
            400,  # 8 grow_repro (Propagator)
            600,  # 9 grow_poison_gland
            # B. movement behavior weights
            1.0,  # 10 prefer_plant
            0.7,  # 11 prefer_enemy
            1.0,  # 12 avoid_poison
            0.01,  # 13 energy_seek_scale
            # C. thresholds + special actions
            0.5,  # 14 move_threshold
            1200,  # 15 reproduce_strength_threshold
            0.30,  # 16 reproduce_give_frac
            1000,  # 17 poison_drop_threshold
            0.25,  # 18 random_walk_prob
            0.4,  # 19 cloak_threshold (fraction of strength)
        ],
        dtype=float,
    )

    # --------------------------------------------
    # Constructor
    # --------------------------------------------
    def __init__(self, dna=None):
        super().__init__()
        SimpleRLV3.__instance_count += 1

        self.dna = np.copy(dna) if dna is not None else np.copy(self.DEFAULT_DNA)

        # organ references
        self.cilia = None
        self.type_sensor = None
        self.energy_sensor = None
        self.life_sensor = None
        self.poison_sensor = None
        self.poison_gland = None
        self.cloak = None
        self.spikes = None
        self.womb = None

        # photoglands count
        self.photoglands = 0

    @classmethod
    def instance_count(cls):
        return SimpleRLV3.__instance_count

    @classmethod
    def destroyed(cls):
        SimpleRLV3.__instance_count -= 1

    # ============================================
    #          TURN LOGIC
    # ============================================
    def do_turn(self):
        self.maybe_grow_organs()
        self.maybe_cloak()
        self.maybe_poison_drop()
        self.maybe_reproduce()
        self.act_move()

    # ============================================
    #        ORGAN GROWTH DECISION SYSTEM
    # ============================================

    def maybe_grow(self, threshold, organ_obj, cls):
        """Grow an organ if:
        - We don't have it
        - Strength > threshold
        """
        if organ_obj is None and self.strength() > threshold:
            new = cls(self)
            return new
        return organ_obj

    def maybe_grow_photogland(self, threshold):
        if self.strength() > threshold:
            PhotoGland(self)
            self.photoglands += 1

    def maybe_grow_organs(self):
        dna = self.dna

        self.cilia = self.maybe_grow(dna[0], self.cilia, Cilia)
        self.type_sensor = self.maybe_grow(dna[1], self.type_sensor, CreatureTypeSensor)
        self.energy_sensor = self.maybe_grow(dna[2], self.energy_sensor, EnergySensor)
        self.life_sensor = self.maybe_grow(dna[3], self.life_sensor, LifeSensor)
        self.poison_sensor = self.maybe_grow(dna[4], self.poison_sensor, PoisonSensor)

        # photoglands (can grow many)
        self.maybe_grow_photogland(dna[5])

        self.spikes = self.maybe_grow(dna[6], self.spikes, Spikes)
        self.cloak = self.maybe_grow(dna[7], self.cloak, Cloaking)
        self.womb = self.maybe_grow(dna[8], self.womb, RLPropagator)
        self.poison_gland = self.maybe_grow(dna[9], self.poison_gland, PoisonGland)

    # ============================================
    #              CLOAK BEHAVIOR
    # ============================================
    def maybe_cloak(self):
        if self.cloak is None:
            return
        strength_frac = self.strength() / Creature.MAX_STRENGTH
        if strength_frac < self.dna[19]:
            self.cloak.cloak()
        else:
            self.cloak.uncloak()

    # ============================================
    #          POISON ATTACK BEHAVIOR
    # ============================================
    def enemy_nearby(self):
        if self.type_sensor is None:
            return False
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, SimpleRLV3):
                return True
        return False

    def maybe_poison_drop(self):
        if self.poison_gland is None:
            return
        if self.strength() < self.dna[17]:
            return
        if not self.enemy_nearby():
            return

        direction = random.choice(list(Direction))
        self.poison_gland.drop_poison(direction, 20)

    # ============================================
    #              REPRODUCTION
    # ============================================
    def maybe_reproduce(self):
        if self.womb is None:
            return
        if self.strength() <= self.dna[15]:
            return
        give = int(self.strength() * self.dna[16])
        direction = Direction.random()
        self.womb.give_birth(give, direction)

    # ============================================
    #            MOVEMENT DECISION ENGINE
    # ============================================
    def act_move(self):
        if self.cilia is None:
            return
        if self.type_sensor is None:
            # cannot evaluate world -> random walk
            if random.random() < self.dna[18]:
                self.cilia.move_in_direction(Direction.random())
            return

        dna = self.dna
        best_score = -9999
        best_dir = None

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            if cell is Plant:
                score += dna[10]
            elif cell not in (Soil, SimpleRLV3):
                score += dna[11]  # prefer_enemy

            if self.poison_sensor:
                if self.poison_sensor.sense(direction):
                    score -= dna[12]

            if self.energy_sensor:
                score += self.energy_sensor.sense(direction) * dna[13]

            if score > best_score:
                best_score = score
                best_dir = direction

        if best_score > dna[14]:
            self.cilia.move_in_direction(best_dir)
        else:
            if random.random() < dna[18]:
                self.cilia.move_in_direction(Direction.random())


# ============================================
#          PROPAGATOR FOR RL BUG
# ============================================


class RLPropagator(Propagator):
    """Children inherit EXACT SAME DNA (no mutation)."""

    __slots__ = ()

    def make_child(self):
        parent = self.host()
        child_dna = np.copy(parent.dna)
        return SimpleRLV3(child_dna)
