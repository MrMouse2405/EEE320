"""
Evolver: a DNA-driven adaptive species

DNA encodes organ mix, behavior weights/thresholds, flags, and mutation params.

Notes:
    - Uses aggressive python optimization as implementing genetic algorithm
      is memory and performance intensive.
"""

import random
from typing import Tuple

from shared import (
    Cilia,
    Cloaking,
    Creature,
    CreatureTypeSensor,
    Direction,
    EnergySensor,
    LifeSensor,
    PhotoGland,
    Plant,
    PoisonSensor,
    Propagator,
    Soil,
    Spikes,
)

# Cache enum iteration and RNG lookups (micro-optimizations on hot loops)
DIRECTIONS = tuple(Direction)
_rand = random.random
_gauss = random.gauss
_choice = random.choice
_uniform = random.uniform
_randint = random.randint

"""
    DNA layout (tuples/lists by index for speed/memory):
      organs      = [cilia, type_sensor, energy_sensor, life_sensor, poison_sensor, photo_count, cloak, spikes, womb]
      weights     = [prefer_plant, prefer_enemy, avoid_poison, energy_seek_scale]
      thresholds  = [move_score, repro_strength_frac, repro_give_frac, weak_cloak_frac]
      flags       = [cloak_when_weak, random_walk_if_stalled]
      mutation    = [weight_sigma, thresh_sigma, flip_flag_prob, toggle_organs_prob, max_photo, max_spikes, max_cilia]
"""
CILIA_IDX = 0
TYPE_SENSOR_IDX = 1
ENERGY_SENSOR_IDX = 2
LIFE_SENSOR_IDX = 3
POISON_SENSOR_IDX = 4
PHOTO_COUNT_IDX = 5
CLOAK_IDX = 6
SPIKES_IDX = 7
WOMB_IDX = 8

PREFER_PLANT_WEIGHT_IDX = 0
PREFER_ENEMY_WEIGHT_IDX = 1
AVOID_POINT_WEIGHT_IDX = 2
ENERGY_SEEK_SCALE_IDX = 3

MOVE_SCORE_IDX = 0
REPRODUCTION_STRENGHT_FRACTION_IDX = 1
REPRODUCTION_GIVE_FRACTION_IDX = 2
WEAK_CLOAK_FRACE = 3

CLOAK_WHEN_WEAK_FRACTION = 0
RANDOM_WALK_IF_STALLED = 1

WEIGHT_SIGMA = 0
THRESHOLD_SIGMA = 1
FLIP_FLAG_PROBABILITY = 2
TOGGLE_ORGANS_PROPABILITY = 3
MAX_PHOTO_IDX = 4


class Evolver(Creature):
    """
    DNA layout (tuples/lists by index for speed/memory):
      organs      = [cilia, type_sensor, energy_sensor, life_sensor, poison_sensor, photo_count, cloak, spikes, womb]
      weights     = [prefer_plant, prefer_enemy, avoid_poison, energy_seek_scale]
      thresholds  = [move_score, repro_strength_frac, repro_give_frac, weak_cloak_frac]
      flags       = [cloak_when_weak, random_walk_if_stalled]
      mutation    = [weight_sigma, thresh_sigma, flip_flag_prob, toggle_organs_prob, max_photo, max_spikes, max_cilia]
    """

    __slots__ = (
        "dna_organs",
        "dna_weights",
        "dna_thresholds",
        "dna_flags",
        "dna_mutation",
        "cilia",
        "type_sensor",
        "energy_sensor",
        "life_sensor",
        "poison_sensor",
        "womb",
        "cloak",
        "spikes",
        "photoglands",
        "lineage_jitter",
    )

    __instance_count = 0
    colour = "#4444dd"

    # Default DNA (tuples so they can be shared; instances copy to lists)
    DEFAULT_ORGANS = (1, 1, 1, 1, 1, 1, 0, 0, 1)
    DEFAULT_WEIGHTS = (1.2, 0.8, 1.5, 0.002)
    DEFAULT_THRESHOLDS = (0.6, 0.70, 0.40, 0.25)
    DEFAULT_FLAGS = (False, True)
    DEFAULT_MUTATION = (0.15, 0.08, 0.06, 0.03, 2, 1, 1)

    def __init__(self, dna: Tuple | None = None):
        super().__init__()
        Evolver.__instance_count += 1

        if dna is None:
            # Copy defaults into per-instance mutable lists
            self.dna_organs = list(self.DEFAULT_ORGANS)
            self.dna_weights = list(self.DEFAULT_WEIGHTS)
            self.dna_thresholds = list(self.DEFAULT_THRESHOLDS)
            self.dna_flags = list(self.DEFAULT_FLAGS)
            self.dna_mutation = list(self.DEFAULT_MUTATION)
        else:
            # Unpack a previously mutated DNA tuple
            (
                self.dna_organs,
                self.dna_weights,
                self.dna_thresholds,
                self.dna_flags,
                self.dna_mutation,
            ) = dna

        # Organ handles (grown lazily when affordable)
        self.cilia = None
        self.type_sensor = None
        self.energy_sensor = None
        self.life_sensor = None
        self.poison_sensor = None
        self.womb = None
        self.cloak = None
        self.spikes = None
        self.photoglands = 0

        # Tiny lineage bias to diversify identical genomes
        self.lineage_jitter = _uniform(-0.05, 0.05)

    # ---- required by framework ----
    @classmethod
    def instance_count(cls):
        return Evolver.__instance_count

    @classmethod
    def destroyed(cls):
        Evolver.__instance_count -= 1

    # ---- main turn ----
    def do_turn(self):
        self._grow_organs()  # build what DNA says, when affordable
        self._maybe_cloak()  # opportunistic stealth if DNA enables it
        self._maybe_reproduce()  # give birth with mutated DNA
        self._act()  # score directions, move/attack, or idle

    # ---------- organ growth ----------
    def _grow_organs(self):
        # Use fresh strength() each check (organ creation spends energy)
        def can_afford(cost: int) -> bool:
            return self.strength() > cost + 10  # safety margin

        o = self.dna_organs  # local alias

        # Movement
        if o[0] and self.cilia is None and can_afford(Cilia.CREATION_COST):
            self.cilia = Cilia(self)

        # Sensors
        if (
            o[1]
            and self.type_sensor is None
            and can_afford(CreatureTypeSensor.CREATION_COST)
        ):
            self.type_sensor = CreatureTypeSensor(self)
        if (
            o[2]
            and self.energy_sensor is None
            and can_afford(EnergySensor.CREATION_COST)
        ):
            self.energy_sensor = EnergySensor(self)
        if o[3] and self.life_sensor is None and can_afford(LifeSensor.CREATION_COST):
            self.life_sensor = LifeSensor(self)
        if (
            o[4]
            and self.poison_sensor is None
            and can_afford(PoisonSensor.CREATION_COST)
        ):
            self.poison_sensor = PoisonSensor(self)

        # Photosynthesis (may allow >1)
        target_photo = o[5]
        while self.photoglands < target_photo and can_afford(PhotoGland.CREATION_COST):
            PhotoGland(self)
            self.photoglands += 1

        # Defense / stealth
        if o[7] and self.spikes is None and can_afford(Spikes.CREATION_COST):
            self.spikes = Spikes(self)
        if o[6] and self.cloak is None and can_afford(Cloaking.CREATION_COST):
            self.cloak = Cloaking(self)

        # Reproduction
        if o[8] and self.womb is None and can_afford(Propagator.CREATION_COST):
            self.womb = EvoPropagator(self)

    # ---------- cloak behavior ----------
    def _maybe_cloak(self):
        # flags[0] = cloak_when_weak; thresholds[3] = weak_cloak_frac
        if not self.cloak or not self.dna_flags[0]:
            return
        weak_gate = self.dna_thresholds[3] * Creature.MAX_STRENGTH
        if self.strength() < weak_gate:
            # Cloak charges use cost; if it kills us, framework handles death
            self.cloak.cloak()
        else:
            # Avoid long-term maintenance while strong
            self.cloak.uncloak()

    # ---------- reproduction ----------
    def _maybe_reproduce(self):
        # thresholds: [move_score, repro_strength_frac, repro_give_frac, weak_cloak_frac]
        if not self.womb:
            return
        strength = self.strength()
        if strength >= self.dna_thresholds[1] * Creature.MAX_STRENGTH:
            give = max(
                Propagator.CREATION_COST + 5, int(strength * self.dna_thresholds[2])
            )
            # Prefer Soil/Plant as nursery; fall back to random
            d = None
            if self.type_sensor:
                for dir_ in DIRECTIONS:
                    t = self.type_sensor.sense(dir_)
                    if t is Soil or t is Plant:
                        d = dir_
                        break
            if d is None:
                d = _choice(DIRECTIONS)
            self.womb.give_birth(give, d)

    # ---------- behavior engine ----------
    def _act(self):
        # Need at least movement + type sensing
        if not (self.cilia and self.type_sensor):
            return

        w = self.dna_weights
        move_threshold = self.dna_thresholds[0]

        best_d = None
        best_score = float("-inf")

        has_poison = self.poison_sensor is not None
        has_energy = self.energy_sensor is not None
        jitter = self.lineage_jitter

        for d in DIRECTIONS:
            # Score each direction once (single sensor reads per dir)
            score = 0.0

            tval = self.type_sensor.sense(d)
            if tval is Plant:
                score += w[0]  # prefer_plant
            elif (tval is not Soil) and (tval is not Evolver):
                score += w[1]  # prefer_enemy (anything non-Soil, non-self)

            if has_poison and self.poison_sensor.sense(d):
                score -= w[2]  # avoid_poison

            if has_energy:
                score += self.energy_sensor.sense(d) * w[3]  # energy_seek_scale

            score += jitter

            if score > best_score:
                best_score = score
                best_d = d

        if best_d and best_score >= move_threshold:
            self.cilia.move_in_direction(best_d)
        elif self.dna_flags[1] and _rand() < 0.25:  # random_walk_if_stalled
            self.cilia.move_in_direction(_choice(DIRECTIONS))


# ---------------- DNA mutation helpers ----------------


def mutate_dna(parent_dna: Tuple) -> Tuple:
    """
    Return a mutated copy of parent's DNA.
    Keeps values within sane bounds to avoid degenerate behavior.
    """
    organs, weights, thresholds, flags, mutation = parent_dna

    # Copy to mutate (lists are fine and cheap here)
    o = list(organs)
    w = list(weights)
    t = list(thresholds)
    f = list(flags)
    m = list(mutation)

    weight_sigma, thresh_sigma, flip_p, toggle_p, max_photo, max_spikes, max_cilia = m

    # Weights: bounded Gaussian noise
    for i in range(len(w)):
        w[i] = max(-5.0, min(5.0, w[i] + _gauss(0.0, weight_sigma)))

    # Thresholds: index 0 is absolute (0..2.5), others are fractions (0.05..0.95)
    for i in range(len(t)):
        newv = t[i] + _gauss(0.0, thresh_sigma)
        if i == 0:
            t[i] = max(0.0, min(2.5, newv))
        else:
            t[i] = max(0.05, min(0.95, newv))

    # Flags: occasional flips
    for i in range(len(f)):
        if _rand() < flip_p:
            f[i] = not f[i]

    # Organs: occasionally toggle some bits / counts
    if _rand() < toggle_p:
        choice = _randint(0, 3)
        if choice == 0:  # photo count +/- 1 within [0, max_photo]
            o[5] = max(0, min(max_photo, o[5] + (_choice((-1, 1)))))
        elif choice == 1:  # spikes toggle within [0, max_spikes]
            o[7] = max(0, min(max_spikes, o[7] ^ 1))
        elif choice == 2:  # cloak toggle (0/1)
            o[6] = o[6] ^ 1
        elif choice == 3:  # cilia stays 0/1 capped
            o[0] = max(0, min(max_cilia, o[0]))

    return (o, w, t, f, m)


class EvoPropagator(Propagator):
    """Propagator that seeds children with mutated DNA."""

    __slots__ = ()

    def make_child(self):
        parent: Evolver = self.host()  # type: ignore
        child_dna = mutate_dna(
            (
                parent.dna_organs,
                parent.dna_weights,
                parent.dna_thresholds,
                parent.dna_flags,
                parent.dna_mutation,
            )
        )
        return Evolver(child_dna)
