"""
    In honour of Prof. Greg Phillips
GregPhillips: a DNA-driven adaptive species

DNA encodes organ mix, behavior weights/thresholds, flags, and mutation params.

Notes:
    - Uses aggressive python optimization as implementing genetic algorithm
    is memory and performance intensive.

Authors: OCdt Syed, OCdt Pabon
"""

import random
from typing import Tuple, override

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

# DNA Array Indices - Organs
CILIA_IDX = 0
TYPE_SENSOR_IDX = 1
ENERGY_SENSOR_IDX = 2
LIFE_SENSOR_IDX = 3
POISON_SENSOR_IDX = 4
PHOTO_COUNT_IDX = 5
CLOAK_IDX = 6
SPIKES_IDX = 7
WOMB_IDX = 8

# DNA Array Indices - Weights
PREFER_PLANT_WEIGHT_IDX = 0
PREFER_ENEMY_WEIGHT_IDX = 1
AVOID_POISON_WEIGHT_IDX = 2
ENERGY_SEEK_SCALE_IDX = 3

# DNA Array Indices - Thresholds
MOVE_SCORE_THRESHOLD_IDX = 0
REPRODUCTION_STRENGTH_FRAC_IDX = 1
REPRODUCTION_GIVE_FRAC_IDX = 2
WEAK_CLOAK_FRAC_IDX = 3

# DNA Array Indices - Flags
CLOAK_WHEN_WEAK_FLAG_IDX = 0
RANDOM_WALK_IF_STALLED_FLAG_IDX = 1

# DNA Array Indices - Mutation Parameters
WEIGHT_SIGMA_IDX = 0
THRESHOLD_SIGMA_IDX = 1
FLIP_FLAG_PROB_IDX = 2
TOGGLE_ORGANS_PROB_IDX = 3
MAX_PHOTO_IDX = 4
MAX_SPIKES_IDX = 5
MAX_CILIA_IDX = 6

# Behavior Constants
ORGAN_GROWTH_SAFETY_MARGIN = 10
MIN_REPRODUCTION_ENERGY = 5
RANDOM_WALK_PROBABILITY = 0.25
LINEAGE_JITTER_MIN = -0.05
LINEAGE_JITTER_MAX = 0.05

# Mutation Bounds
MIN_WEIGHT_VALUE = -5.0
MAX_WEIGHT_VALUE = 5.0
MIN_THRESHOLD_FRAC = 0.05
MAX_THRESHOLD_FRAC = 0.95
MIN_MOVE_SCORE = 0.0
MAX_MOVE_SCORE = 2.5
MIN_ORGAN_COUNT = 0

# Mutation Toggle Choices
TOGGLE_PHOTO_COUNT = 0
TOGGLE_SPIKES = 1
TOGGLE_CLOAK = 2
TOGGLE_CILIA = 3
NUM_TOGGLE_CHOICES = 4

# COST
PHOTO_COST = PhotoGland.CREATION_COST
CILIA_COST = Cilia.CREATION_COST
CREATURE_TYPE_SENSOR_COST = CreatureTypeSensor.CREATION_COST
ENERGY_SENSOR_COST = EnergySensor.CREATION_COST
LIFE_SENSOR_COST = LifeSensor.CREATION_COST
POISON_SENSOR_COST = PoisonSensor.CREATION_COST
SPIKES_COST = Spikes.CREATION_COST
CLOAKING_COST = Cloaking.CREATION_COST
PROPAGATOR_COST = Propagator.CREATION_COST


# In honour of Prof. Greg Phillips
class GregPhillips(Creature):
    """
    DNA-driven adaptive creature with genetic mutation system.

    DNA layout (tuples/lists by index for speed/memory):
      organs      = [cilia, type_sensor, energy_sensor, life_sensor, poison_sensor,
                     photo_count, cloak, spikes, womb]
      weights     = [prefer_plant, prefer_enemy, avoid_poison, energy_seek_scale]
      thresholds  = [move_score, repro_strength_frac, repro_give_frac, weak_cloak_frac]
      flags       = [cloak_when_weak, random_walk_if_stalled]
      mutation    = [weight_sigma, thresh_sigma, flip_flag_prob, toggle_organs_prob,
                     max_photo, max_spikes, max_cilia]
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
        GregPhillips.__instance_count += 1

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
        self.lineage_jitter = _uniform(LINEAGE_JITTER_MIN, LINEAGE_JITTER_MAX)

    @classmethod
    def instance_count(cls) -> int:  # type: ignore
        return GregPhillips.__instance_count

    @override
    def destroyed(self):
        GregPhillips.__instance_count -= 1

    def do_turn(self):
        self._grow_organs()  # build what DNA says, when affordable
        self._maybe_cloak()  # opportunistic stealth if DNA enables it
        self._maybe_reproduce()  # give birth with mutated DNA
        self._act()  # score directions, move/attack, or idle

    # ---------- organ growth ----------
    def _grow_organs(self):
        """Grow organs based on DNA when creature has sufficient energy."""
        organs = self.dna_organs
        current_strength = self.strength()

        def can_afford(cost: int) -> bool:
            return current_strength > cost + ORGAN_GROWTH_SAFETY_MARGIN

        # Movement organ
        if organs[CILIA_IDX] and self.cilia is None and can_afford(CILIA_COST):
            self.cilia = Cilia(self)
            current_strength = self.strength()

        # Sensors - batch check to avoid repeated lookups
        if (
            self.type_sensor is None
            and organs[TYPE_SENSOR_IDX]
            and can_afford(CREATURE_TYPE_SENSOR_COST)
        ):
            self.type_sensor = CreatureTypeSensor(self)
            current_strength = self.strength()

        if (
            self.energy_sensor is None
            and organs[ENERGY_SENSOR_IDX]
            and can_afford(ENERGY_SENSOR_COST)
        ):
            self.energy_sensor = EnergySensor(self)
            current_strength = self.strength()

        if (
            self.life_sensor is None
            and organs[LIFE_SENSOR_IDX]
            and can_afford(LIFE_SENSOR_COST)
        ):
            self.life_sensor = LifeSensor(self)
            current_strength = self.strength()

        if (
            self.poison_sensor is None
            and organs[POISON_SENSOR_IDX]
            and can_afford(POISON_SENSOR_COST)
        ):
            self.poison_sensor = PoisonSensor(self)
            current_strength = self.strength()

        # Photosynthesis (may allow >1)
        target_photo = organs[PHOTO_COUNT_IDX]
        photo_cost = PHOTO_COST
        while (
            self.photoglands < target_photo
            and current_strength > photo_cost + ORGAN_GROWTH_SAFETY_MARGIN
        ):
            PhotoGland(self)
            self.photoglands += 1
            current_strength = self.strength()

        # Defense / stealth
        if self.spikes is None and organs[SPIKES_IDX] and can_afford(SPIKES_COST):
            self.spikes = Spikes(self)
            current_strength = self.strength()

        if self.cloak is None and organs[CLOAK_IDX] and can_afford(CLOAKING_COST):
            self.cloak = Cloaking(self)
            current_strength = self.strength()

        # Reproduction
        if self.womb is None and organs[WOMB_IDX] and can_afford(PROPAGATOR_COST):
            self.womb = EvoPropagator(self)

    # ---------- cloak behavior ----------
    def _maybe_cloak(self):
        """Activate cloaking when weak if DNA enables this behavior."""
        if not (self.cloak and self.dna_flags[CLOAK_WHEN_WEAK_FLAG_IDX]):
            return

        weak_threshold = (
            self.dna_thresholds[WEAK_CLOAK_FRAC_IDX] * Creature.MAX_STRENGTH
        )
        if self.strength() < weak_threshold:
            # Cloak charges use cost; if it kills us, framework handles death
            self.cloak.cloak()
        else:
            # Avoid long-term maintenance while strong
            self.cloak.uncloak()

    # ---------- reproduction ----------
    def _maybe_reproduce(self):
        """Reproduce when strength threshold is met, giving energy to offspring."""
        if not self.womb:
            return

        strength = self.strength()
        min_repro_strength = (
            self.dna_thresholds[REPRODUCTION_STRENGTH_FRAC_IDX] * Creature.MAX_STRENGTH
        )

        if strength >= min_repro_strength:
            # Calculate energy to give to offspring
            energy_frac = self.dna_thresholds[REPRODUCTION_GIVE_FRAC_IDX]
            min_give = PROPAGATOR_COST + MIN_REPRODUCTION_ENERGY
            give = max(min_give, int(strength * energy_frac))

            # Prefer Soil/Plant as nursery; fall back to random
            direction = None
            if self.type_sensor:
                for dir_ in DIRECTIONS:
                    cell_type = self.type_sensor.sense(dir_)
                    if cell_type is Soil or cell_type is Plant:
                        direction = dir_
                        break

            if direction is None:
                direction = _choice(DIRECTIONS)

            self.womb.give_birth(give, direction)

    # ---------- behavior engine ----------
    def _act(self):
        """Score all directions and move/attack in best direction, or random walk if stalled."""
        # Need at least movement + type sensing
        if not (self.cilia and self.type_sensor):
            return

        weights = self.dna_weights
        move_threshold = self.dna_thresholds[MOVE_SCORE_THRESHOLD_IDX]

        # Cache these for hot loop
        has_poison = self.poison_sensor is not None
        has_energy = self.energy_sensor is not None
        jitter = self.lineage_jitter

        # Cache weight lookups
        plant_weight = weights[PREFER_PLANT_WEIGHT_IDX]
        enemy_weight = weights[PREFER_ENEMY_WEIGHT_IDX]
        poison_weight = weights[AVOID_POISON_WEIGHT_IDX]
        energy_scale = weights[ENERGY_SEEK_SCALE_IDX]

        best_direction = None
        best_score = float("-inf")

        for direction in DIRECTIONS:
            # Score each direction once (single sensor reads per dir)
            score = 0.0

            # Type-based scoring
            cell_type = self.type_sensor.sense(direction)
            if cell_type is Plant:
                score += plant_weight
            elif (cell_type is not Soil) and (cell_type is not GregPhillips):
                # Prefer enemy (anything non-Soil, non-self)
                score += enemy_weight

            # Poison avoidance
            if has_poison and self.poison_sensor.sense(direction):  # type: ignore
                score -= poison_weight

            # Energy seeking
            if has_energy:
                score += self.energy_sensor.sense(direction) * energy_scale  # type: ignore

            # Lineage diversity
            score += jitter

            if score > best_score:
                best_score = score
                best_direction = direction

        # Execute best move or random walk
        if best_direction and best_score >= move_threshold:
            self.cilia.move_in_direction(best_direction)
        elif (
            self.dna_flags[RANDOM_WALK_IF_STALLED_FLAG_IDX]
            and _rand() < RANDOM_WALK_PROBABILITY
        ):
            self.cilia.move_in_direction(_choice(DIRECTIONS))


# ---------------- DNA mutation helpers ----------------


def mutate_dna(parent_dna: Tuple) -> Tuple:
    """
    Return a mutated copy of parent's DNA.
    Keeps values within sane bounds to avoid degenerate behavior.
    """
    organs, weights, thresholds, flags, mutation = parent_dna

    new_organs = list(organs)
    new_weights = list(weights)
    new_thresholds = list(thresholds)
    new_flags = list(flags)
    new_mutation = list(mutation)

    weight_sigma = mutation[WEIGHT_SIGMA_IDX]
    thresh_sigma = mutation[THRESHOLD_SIGMA_IDX]
    flip_prob = mutation[FLIP_FLAG_PROB_IDX]
    toggle_prob = mutation[TOGGLE_ORGANS_PROB_IDX]
    max_photo = mutation[MAX_PHOTO_IDX]
    max_spikes = mutation[MAX_SPIKES_IDX]
    max_cilia = mutation[MAX_CILIA_IDX]

    # Mutate weights with bounded Gaussian noise
    for i in range(len(new_weights)):
        new_weights[i] = max(
            MIN_WEIGHT_VALUE,
            min(MAX_WEIGHT_VALUE, new_weights[i] + _gauss(0.0, weight_sigma)),
        )

    # Mutate thresholds: index 0 is absolute score, others are fractions
    for i in range(len(new_thresholds)):
        new_value = new_thresholds[i] + _gauss(0.0, thresh_sigma)
        if i == MOVE_SCORE_THRESHOLD_IDX:
            new_thresholds[i] = max(MIN_MOVE_SCORE, min(MAX_MOVE_SCORE, new_value))
        else:
            new_thresholds[i] = max(
                MIN_THRESHOLD_FRAC, min(MAX_THRESHOLD_FRAC, new_value)
            )

    # Mutate flags: occasional random flips
    for i in range(len(new_flags)):
        if _rand() < flip_prob:
            new_flags[i] = not new_flags[i]

    # Mutate organs: occasionally toggle some bits / counts
    if _rand() < toggle_prob:
        toggle_choice = _randint(0, NUM_TOGGLE_CHOICES - 1)

        if toggle_choice == TOGGLE_PHOTO_COUNT:
            # Photo count +/- 1 within [0, max_photo]
            delta = _choice((-1, 1))
            new_organs[PHOTO_COUNT_IDX] = max(
                MIN_ORGAN_COUNT, min(max_photo, new_organs[PHOTO_COUNT_IDX] + delta)
            )
        elif toggle_choice == TOGGLE_SPIKES:
            # Spikes toggle within [0, max_spikes]
            new_organs[SPIKES_IDX] = max(
                MIN_ORGAN_COUNT, min(max_spikes, new_organs[SPIKES_IDX] ^ 1)
            )
        elif toggle_choice == TOGGLE_CLOAK:
            # Cloak toggle (0/1)
            new_organs[CLOAK_IDX] = new_organs[CLOAK_IDX] ^ 1
        elif toggle_choice == TOGGLE_CILIA:
            # Cilia stays 0/1 capped
            new_organs[CILIA_IDX] = max(
                MIN_ORGAN_COUNT, min(max_cilia, new_organs[CILIA_IDX])
            )

    return (new_organs, new_weights, new_thresholds, new_flags, new_mutation)


class EvoPropagator(Propagator):
    """Propagator that seeds children with mutated DNA."""

    __slots__ = ()

    @override
    def make_child(self):
        """Create offspring with mutated DNA from parent."""
        parent: GregPhillips = self.host()  # type: ignore (this is to shut pyright up)
        child_dna = mutate_dna(
            (
                parent.dna_organs,
                parent.dna_weights,
                parent.dna_thresholds,
                parent.dna_flags,
                parent.dna_mutation,
            )
        )
        return GregPhillips(child_dna)
