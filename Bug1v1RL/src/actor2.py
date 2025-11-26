"""
DNA_CMA_ES_BUG_INFERENCE - Phase-Based Adaptive Strategy (Inference Only)

This is the deployment version of the trained bug:
- Loads best DNA from training file
- No reward scoring (pure behavior)
- Phase-based strategy (early/mid/late game)
- Proper cilia management
"""

import os
import random
from typing import override

import numpy as np

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
    PoisonGland,
    PoisonSensor,
    Propagator,
    Soil,
    Spikes,
)


class DNA_CMA_ES_BUG_INFERENCE(Creature):
    """
    Inference-only version of the phase-based trained bug.
    Loads best DNA from training and uses it without any reward scoring.

    Phase tracking uses individual bug's age - no framework modification needed.
    """

    __instance_count = 0

    # Load from the training file
    TOP_FILE = "dna2_top10.npy"
    colour = "#4444dd"  # Blue to distinguish from training red

    # Phase transition turn (based on bug age)
    PHASE_TRANSITION = 500

    # Default DNA - Phase-based (64 values)
    # Fallback if no trained weights exist
    DEFAULT_DNA = np.array(
        [
            # ========== EARLY GAME (indices 0-31) ==========
            # ORGAN THRESHOLDS - minimum strength after creation
            200,  # [0] Cilia threshold
            100,  # [1] Type sensor threshold
            300,  # [2] Energy sensor threshold
            800,  # [3] Life sensor threshold
            600,  # [4] Poison sensor threshold
            350,  # [5] PhotoGland threshold
            250,  # [6] Spikes threshold
            1200,  # [7] Cloaking threshold
            300,  # [8] Womb threshold
            1000,  # [9] Poison gland threshold
            4,  # [10] Target cilia count
            2,  # [11] Target photogland count
            0,  # [12] Reserved
            0.85,  # [13] Combat weight
            0.5,  # [14] Reproduction weight
            0.05,  # [15] Poison weight
            0.05,  # [16] Cloak weight
            0.2,  # [17] Foraging weight
            3.0,  # [18] Enemy attraction
            2.5,  # [19] Plant attraction
            -2.0,  # [20] Poison avoidance
            0.02,  # [21] Energy attraction
            0.9,  # [22] Move probability
            0.7,  # [23] Min strength ratio
            500,  # [24] Min absolute strength
            0.2,  # [25] Cloak threshold
            1.4,  # [26] Aggressive pursuit ratio
            800,  # [27] Min strength to reproduce
            0.35,  # [28] Energy fraction
            5,  # [29] Max offspring
            0.35,  # [30] Population scaling
            0.5,  # [31] Reproduction probability
            # ========== LATE GAME (indices 32-63) ==========
            150,  # [32] Cilia threshold
            50,  # [33] Type sensor threshold
            200,  # [34] Energy sensor threshold
            500,  # [35] Life sensor threshold
            400,  # [36] Poison sensor threshold
            300,  # [37] PhotoGland threshold
            200,  # [38] Spikes threshold
            500,  # [39] Cloaking threshold
            250,  # [40] Womb threshold
            600,  # [41] Poison gland threshold
            6,  # [42] Target cilia count
            2,  # [43] Target photogland count
            0,  # [44] Reserved
            0.95,  # [45] Combat weight
            0.2,  # [46] Reproduction weight
            0.15,  # [47] Poison weight
            0.1,  # [48] Cloak weight
            0.1,  # [49] Foraging weight
            4.0,  # [50] Enemy attraction
            1.0,  # [51] Plant attraction
            -1.5,  # [52] Poison avoidance
            0.01,  # [53] Energy attraction
            0.95,  # [54] Move probability
            0.5,  # [55] Min strength ratio
            350,  # [56] Min absolute strength
            0.15,  # [57] Cloak threshold
            1.2,  # [58] Aggressive pursuit ratio
            1000,  # [59] Min strength to reproduce
            0.3,  # [60] Energy fraction
            3,  # [61] Max offspring
            0.5,  # [62] Population scaling
            0.25,  # [63] Reproduction probability
        ],
        dtype=float,
    )

    def __init__(self, dna=None):
        super().__init__()
        DNA_CMA_ES_BUG_INFERENCE.__instance_count += 1

        # Use provided DNA or load best from file
        if dna is not None:
            self.dna = np.copy(dna)
        else:
            self.dna = self.load_best_dna()

        # Organs - store actual references for cilia
        self.cilia_list = []  # List of actual Cilia objects
        self.type_sensor = None
        self.energy_sensor = None
        self.life_sensor = None
        self.poison_sensor = None
        self.poison_gland = None
        self.cloak = None
        self.spikes = None
        self.womb = None
        self.photoglands = 0

        # State tracking
        self.offspring_count = 0
        self.age = 0

    # ======================================================
    #              INSTANCE COUNTING
    # ======================================================
    @classmethod
    def instance_count(cls):
        return DNA_CMA_ES_BUG_INFERENCE.__instance_count

    @classmethod
    def destroyed(cls):
        DNA_CMA_ES_BUG_INFERENCE.__instance_count -= 1

    # ======================================================
    #              LOAD BEST DNA
    # ======================================================
    @classmethod
    def load_best_dna(cls):
        """Load the best DNA from training file."""
        if os.path.exists(cls.TOP_FILE):
            try:
                top_dna_list = list(np.load(cls.TOP_FILE, allow_pickle=True))
                if len(top_dna_list) > 0:
                    # Get the best DNA (highest reward)
                    best_entry = top_dna_list[0]
                    best_dna = best_entry[1]
                    print(f"[INFERENCE] Loaded best DNA with reward: {best_entry[0]}")
                    return np.copy(best_dna)
            except Exception as e:
                print(f"[INFERENCE] Failed to load DNA: {e}")

        print("[INFERENCE] No trained DNA found, using default")
        return np.copy(cls.DEFAULT_DNA)

    # ======================================================
    #              PHASE-BASED DNA ACCESS
    # ======================================================
    def get_phase_weight(self):
        """Returns interpolation weight: 0 = early game, 1 = late game

        Uses individual bug's age as proxy for game phase.
        This works because all bugs age together each turn.
        """
        # Use this bug's age as the phase indicator
        # Older bugs = later in game
        turn = self.age
        if turn <= 0:
            return 0.0
        elif turn >= self.PHASE_TRANSITION:
            return 1.0
        else:
            return turn / self.PHASE_TRANSITION

    def get_param(self, early_idx, late_idx=None):
        """Get parameter interpolated between early and late game"""
        if late_idx is None:
            late_idx = early_idx + 32

        phase = self.get_phase_weight()
        early_val = self.dna[early_idx]
        late_val = self.dna[late_idx]
        return early_val + phase * (late_val - early_val)

    # ======================================================
    #                       TURN
    # ======================================================
    def do_turn(self):
        """Execute turn without any reward scoring."""
        self.age += 1

        # Grow organs based on phase
        self.grow_organs_adaptive()

        # Execute actions based on phase-weighted priorities
        self.execute_actions()

    # ======================================================
    #                  ORGAN MANAGEMENT
    # ======================================================
    def count_organs(self):
        """Count total organs"""
        count = len(self.cilia_list) + self.photoglands
        if self.type_sensor:
            count += 1
        if self.energy_sensor:
            count += 1
        if self.life_sensor:
            count += 1
        if self.poison_sensor:
            count += 1
        if self.spikes:
            count += 1
        if self.cloak:
            count += 1
        if self.womb:
            count += 1
        if self.poison_gland:
            count += 1
        return count

    def can_grow_organ(self):
        return self.count_organs() < Creature.MAX_ORGANS

    def grow_singleton(self, threshold_early, organ_ref, organ_class):
        """Grow a singleton organ if conditions met"""
        if organ_ref is not None:
            return organ_ref

        threshold = self.get_param(threshold_early)
        creation_cost = organ_class.CREATION_COST

        if self.strength() - creation_cost >= threshold and self.can_grow_organ():
            return organ_class(self)
        return None

    def grow_organs_adaptive(self):
        """Grow organs based on game phase and current state"""

        # ALWAYS prioritize type sensor (need to see enemies)
        self.type_sensor = self.grow_singleton(1, self.type_sensor, CreatureTypeSensor)

        # Spikes early for defense
        self.spikes = self.grow_singleton(6, self.spikes, Spikes)

        # Energy sensor for combat decisions
        self.energy_sensor = self.grow_singleton(2, self.energy_sensor, EnergySensor)

        # Cilia for movement (multiple)
        target_cilia = int(self.get_param(10))
        cilia_threshold = self.get_param(0)
        while (
            len(self.cilia_list) < target_cilia
            and self.strength() - Cilia.CREATION_COST >= cilia_threshold
            and self.can_grow_organ()
        ):
            new_cilia = Cilia(self)
            self.cilia_list.append(new_cilia)

        # PhotoGlands for energy (multiple)
        target_photo = int(self.get_param(11))
        photo_threshold = self.get_param(5)
        while (
            self.photoglands < target_photo
            and self.strength() - PhotoGland.CREATION_COST >= photo_threshold
            and self.can_grow_organ()
        ):
            PhotoGland(self)
            self.photoglands += 1

        # Womb for reproduction
        self.womb = self.grow_singleton(8, self.womb, InferencePropagator)

        # Optional organs based on phase
        phase = self.get_phase_weight()

        # Poison sensor becomes more important late game
        if phase > 0.3:
            self.poison_sensor = self.grow_singleton(
                4, self.poison_sensor, PoisonSensor
            )

        # Poison gland for area denial
        if phase > 0.4:
            self.poison_gland = self.grow_singleton(9, self.poison_gland, PoisonGland)

        # Cloaking is expensive - only if we have room
        if self.can_grow_organ() and self.count_organs() <= 7:
            self.cloak = self.grow_singleton(7, self.cloak, Cloaking)

    # ======================================================
    #                  ACTION EXECUTION
    # ======================================================
    def execute_actions(self):
        """Execute actions based on weighted priorities"""
        combat_weight = self.get_param(13)
        repro_weight = self.get_param(14)
        poison_weight = self.get_param(15)
        cloak_weight = self.get_param(16)

        # Build action list with weights
        actions = [
            (combat_weight, self.act_combat),
            (repro_weight, self.act_reproduce),
            (poison_weight, self.act_poison),
            (cloak_weight, self.act_cloak),
        ]

        # Sort by weight
        actions.sort(key=lambda x: x[0], reverse=True)

        # Execute all actions with weight > 0.05
        for weight, action in actions:
            if weight > 0.05:
                action()

    # ======================================================
    #                  COMBAT / MOVEMENT
    # ======================================================
    def get_available_cilia(self):
        """Get cilia that haven't been used this turn"""
        return [c for c in self.cilia_list if c.f_uses_this_turn() == 0]

    def act_combat(self):
        """Main combat/movement action"""
        available = self.get_available_cilia()
        if not available:
            return

        move_prob = self.get_param(22)
        enemy_attraction = self.get_param(18)
        plant_attraction = self.get_param(19)
        poison_avoidance = self.get_param(20)
        min_ratio = self.get_param(23)
        min_strength = self.get_param(24)

        # Determine number of moves to make
        phase = self.get_phase_weight()
        max_moves = min(len(available), int(2 + phase * 4))  # 2-6 moves based on phase

        for _ in range(max_moves):
            available = self.get_available_cilia()
            if not available:
                break

            # Find best direction
            best_dir, best_score = self.evaluate_directions(
                enemy_attraction,
                plant_attraction,
                poison_avoidance,
                min_ratio,
                min_strength,
            )

            if best_dir is None:
                # No sensor - move randomly
                if random.random() < move_prob * 0.5:
                    available[0].move_in_direction(Direction.random())
                break

            # Move if score is acceptable
            if best_score > -50 and random.random() < move_prob:
                available[0].move_in_direction(best_dir)

    def evaluate_directions(
        self,
        enemy_attraction,
        plant_attraction,
        poison_avoidance,
        min_ratio,
        min_strength,
    ):
        """Evaluate all 8 directions and return best one"""
        if self.type_sensor is None:
            return None, 0

        best_score = -9999
        best_dir = None

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            # Enemy targeting
            if cell not in (Soil, Plant, DNA_CMA_ES_BUG_INFERENCE, None):
                enemy_strength = 0
                if self.energy_sensor:
                    enemy_strength = self.energy_sensor.sense(direction)

                strength_ratio = self.strength() / max(enemy_strength, 1)

                if strength_ratio >= min_ratio and self.strength() >= min_strength:
                    # We can take this enemy
                    score += enemy_attraction * 100
                    if strength_ratio >= 2.0:
                        score += 150  # Easy kill bonus
                else:
                    # Avoid stronger enemies
                    score -= 150

            # Plant attraction (food)
            elif cell is Plant:
                score += plant_attraction * 20

            # Poison avoidance
            if self.poison_sensor and self.poison_sensor.sense(direction):
                score += poison_avoidance * 30

            # Energy bonus for targets
            if self.energy_sensor:
                energy = self.energy_sensor.sense(direction)
                if cell is Plant:
                    score += energy * 0.01

            if score > best_score:
                best_score = score
                best_dir = direction

        return best_dir, best_score

    # ======================================================
    #                  REPRODUCTION
    # ======================================================
    def act_reproduce(self):
        """Attempt to reproduce"""
        if self.womb is None:
            return

        max_offspring = int(self.get_param(29))
        if self.offspring_count >= max_offspring:
            return

        min_strength = self.get_param(27)
        if self.strength() <= min_strength:
            return

        repro_prob = self.get_param(31)
        if random.random() > repro_prob:
            return

        # Population check - don't overcrowd
        pop = self.instance_count()
        pop_scale = self.get_param(30)
        if pop > 10 and self.strength() < min_strength * (1 + pop * pop_scale * 0.01):
            return

        # Find empty direction
        birth_dir = Direction.random()
        if self.type_sensor:
            for d in Direction:
                cell = self.type_sensor.sense(d)
                if cell is Soil or cell is Plant:
                    birth_dir = d
                    break

        energy_fraction = self.get_param(28)
        give = int(self.strength() * energy_fraction)

        before = self.instance_count()
        self.womb.give_birth(give, birth_dir)
        after = self.instance_count()

        if after > before:
            self.offspring_count += 1

    # ======================================================
    #                  POISON
    # ======================================================
    def act_poison(self):
        """Use poison gland if appropriate"""
        if self.poison_gland is None or self.type_sensor is None:
            return

        if self.strength() < 600:
            return

        # Look for adjacent enemies
        for d in Direction:
            cell = self.type_sensor.sense(d)
            if cell not in (Soil, Plant, None, DNA_CMA_ES_BUG_INFERENCE):
                # Enemy adjacent - drop poison
                if random.random() < 0.5:
                    self.poison_gland.drop_poison(d, 25)
                return

    # ======================================================
    #                  CLOAK
    # ======================================================
    def act_cloak(self):
        """Manage cloaking based on strength"""
        if self.cloak is None:
            return

        cloak_threshold = self.get_param(25)
        strength_frac = self.strength() / Creature.MAX_STRENGTH

        if strength_frac < cloak_threshold:
            self.cloak.cloak()
        else:
            self.cloak.uncloak()


# ======================================================
#     Propagator - passes DNA to children
# ======================================================
class InferencePropagator(Propagator):
    __slots__ = ()

    def make_child(self):
        return DNA_CMA_ES_BUG_INFERENCE(np.copy(self.host().dna))  # type: ignore
