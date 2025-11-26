"""
DNA_CMA_ES_BUG_RED - Phase-Based Adaptive Strategy

Key improvements:
1. Phase-based DNA parameters (early/mid/late game)
2. Proper cilia organ management (store references)
3. Population-aware decision making
4. Win-focused reward shaping (survival + domination)
5. Adaptive organ growth priorities
6. Turn counter for temporal awareness
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


class DNA_CMA_ES_BUG_RED(Creature):
    __instance_count = 0

    TOP_FILE = "dna_top10.npy"
    reward_score = 0
    colour = "#dd4444"

    # ======================================================
    #                 REWARD CONSTANTS
    # ======================================================
    # WINNING IS EVERYTHING - heavily skewed toward outcomes
    R_WIN = +500000  # Massive reward for winning
    R_LOSS = -200000  # Heavy penalty for losing
    R_TIMEOUT_WIN = +100000  # Good reward for dominating at timeout
    R_TIMEOUT_LOSE = -100000  # Heavy penalty for losing at timeout
    R_TIMEOUT_DRAW = -50000  # Draws are bad - should be winning

    # Combat - moderate rewards
    R_KILL = +1000  # Good kill reward
    R_DEATH = -500  # Death penalty
    R_DAMAGE_DEALT = +1.0
    R_DAMAGE_TAKEN = -0.5

    # Reproduction - encourage sustainable growth
    R_SUCCESS_REPRO = +100
    R_USELESS_REPRO = -50

    # Population dominance bonus (per turn)
    R_POP_ADVANTAGE = +5  # Per bug advantage

    # Survival bonus (scales with time)
    R_SURVIVE = +0.1

    # ======================================================
    #         DNA CONFIG - PHASE-BASED (64 values)
    # ======================================================
    # DNA is split into phases:
    # [0-31]  = EARLY game (turns 0-500)
    # [32-63] = LATE game (turns 500+)
    # Linear interpolation between phases

    DEFAULT_DNA = np.array(
        [
            # ========== EARLY GAME (indices 0-31) ==========
            # ORGAN THRESHOLDS - minimum strength after creation
            # Lower values = more aggressive growth
            200,  # [0] Cilia threshold - grow movement early
            100,  # [1] Type sensor threshold - MUST SEE
            300,  # [2] Energy sensor threshold
            800,  # [3] Life sensor threshold (skip early)
            600,  # [4] Poison sensor threshold (skip early)
            350,  # [5] PhotoGland threshold
            250,  # [6] Spikes threshold - defense matters
            1200,  # [7] Cloaking threshold (skip early)
            300,  # [8] Womb threshold - reproduce early
            1000,  # [9] Poison gland threshold (skip early)
            # ORGAN QUANTITIES (10-12)
            4,  # [10] Target cilia count - MOVE FAST
            2,  # [11] Target photogland count
            0,  # [12] Reserved
            # ACTION WEIGHTS (13-17)
            0.85,  # [13] Combat weight - HIGH
            0.5,  # [14] Reproduction weight - populate
            0.05,  # [15] Poison weight - skip
            0.05,  # [16] Cloak weight - skip
            0.2,  # [17] Foraging weight
            # MOVEMENT PARAMS (18-22)
            3.0,  # [18] Enemy attraction - HUNT!
            2.5,  # [19] Plant attraction - eat plants
            -2.0,  # [20] Poison avoidance
            0.02,  # [21] Energy attraction
            0.9,  # [22] Move probability - ALWAYS MOVE
            # COMBAT PARAMS (23-26)
            0.7,  # [23] Min strength ratio - be bold
            500,  # [24] Min absolute strength
            0.2,  # [25] Cloak threshold
            1.4,  # [26] Aggressive pursuit ratio
            # REPRODUCTION PARAMS (27-31)
            800,  # [27] Min strength to reproduce
            0.35,  # [28] Energy fraction to offspring
            5,  # [29] Max offspring per bug
            0.35,  # [30] Population scaling
            0.5,  # [31] Reproduction probability
            # ========== LATE GAME (indices 32-63) ==========
            150,  # [32] Cilia threshold - very aggressive
            50,  # [33] Type sensor threshold
            200,  # [34] Energy sensor threshold
            500,  # [35] Life sensor threshold
            400,  # [36] Poison sensor threshold
            300,  # [37] PhotoGland threshold
            200,  # [38] Spikes threshold
            500,  # [39] Cloaking threshold
            250,  # [40] Womb threshold
            600,  # [41] Poison gland threshold
            # ORGAN QUANTITIES (42-44)
            6,  # [42] Target cilia count - MAX HUNTING
            2,  # [43] Target photogland count
            0,  # [44] Reserved
            # ACTION WEIGHTS (45-49)
            0.95,  # [45] Combat weight - MAXIMUM
            0.2,  # [46] Reproduction weight
            0.15,  # [47] Poison weight
            0.1,  # [48] Cloak weight
            0.1,  # [49] Foraging weight
            # MOVEMENT PARAMS (50-54)
            4.0,  # [50] Enemy attraction - MAXIMUM
            1.0,  # [51] Plant attraction
            -1.5,  # [52] Poison avoidance
            0.01,  # [53] Energy attraction
            0.95,  # [54] Move probability
            # COMBAT PARAMS (55-58)
            0.5,  # [55] Min strength ratio - very aggressive
            350,  # [56] Min absolute strength
            0.15,  # [57] Cloak threshold
            1.2,  # [58] Aggressive pursuit ratio
            # REPRODUCTION PARAMS (59-63)
            1000,  # [59] Min strength to reproduce
            0.3,  # [60] Energy fraction to offspring
            3,  # [61] Max offspring
            0.5,  # [62] Population scaling
            0.25,  # [63] Reproduction probability
        ],
        dtype=float,
    )

    # Phase transition turn
    PHASE_TRANSITION = 500

    def __init__(self, dna=None):
        super().__init__()
        DNA_CMA_ES_BUG_RED.__instance_count += 1
        self.dna = np.copy(dna) if dna is not None else np.copy(self.DEFAULT_DNA)

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
        self.kills = 0
        self.age = 0

    # ======================================================
    #              INSTANCE COUNTING
    # ======================================================
    @classmethod
    def instance_count(cls):
        return DNA_CMA_ES_BUG_RED.__instance_count

    @classmethod
    def destroyed(cls):
        DNA_CMA_ES_BUG_RED.__instance_count -= 1

    # ======================================================
    #              PHASE-BASED DNA ACCESS
    # ======================================================
    def get_phase_weight(self):
        """Returns interpolation weight: 0 = early game, 1 = late game

        Uses individual bug's age as proxy for game phase.
        This works because bugs that survive longer are in later game phases.
        New babies start at phase 0 and adapt as they age.
        """
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
    #              REWARD METHODS
    # ======================================================
    @classmethod
    def reward_win(cls):
        cls.reward_score += cls.R_WIN

    @classmethod
    def reward_loss(cls):
        cls.reward_score += cls.R_LOSS

    @classmethod
    def reward_timeout(cls, my_count, opp_count):
        """Called when match times out - reward based on population"""
        if my_count > opp_count:
            # Winning at timeout - good but not as good as real win
            advantage = my_count - opp_count
            cls.reward_score += cls.R_TIMEOUT_WIN + (advantage * 1000)
        elif my_count < opp_count:
            # Losing at timeout - bad
            disadvantage = opp_count - my_count
            cls.reward_score += cls.R_TIMEOUT_LOSE - (disadvantage * 1000)
        else:
            # Draw - not good, should be winning
            cls.reward_score += cls.R_TIMEOUT_DRAW

    # ======================================================
    #                     DEATH
    # ======================================================
    @override
    def f_die(self):
        DNA_CMA_ES_BUG_RED.reward_score += DNA_CMA_ES_BUG_RED.R_DEATH
        super().f_die()

    # ======================================================
    #                     COMBAT
    # ======================================================
    @override
    def f_attack(self, defender):
        my_before = self.strength()
        def_before = defender.strength()

        result = super().f_attack(defender)

        my_after = self.strength()
        def_after = defender.strength()

        # Damage tracking
        dmg_to_enemy = max(0, def_before - def_after)
        dmg_to_me = max(0, my_before - my_after)

        DNA_CMA_ES_BUG_RED.reward_score += dmg_to_enemy * self.R_DAMAGE_DEALT
        DNA_CMA_ES_BUG_RED.reward_score += dmg_to_me * self.R_DAMAGE_TAKEN

        # Kill bonus - only for killing actual enemies (not plants/soil)
        if result is self and def_before > 0:
            if type(defender) not in (Soil, Plant, DNA_CMA_ES_BUG_RED):
                DNA_CMA_ES_BUG_RED.reward_score += self.R_KILL
                self.kills += 1

        return result

    # ======================================================
    #                       TURN
    # ======================================================
    def do_turn(self):
        self.age += 1

        # Survival reward (scales with game progress)
        phase = self.get_phase_weight()
        DNA_CMA_ES_BUG_RED.reward_score += self.R_SURVIVE * (1 + phase)

        # Population advantage bonus
        my_pop = self.instance_count()
        # Estimate enemy population (total creatures - my bugs - plants/soil estimate)
        # This is approximate but helps guide behavior

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
        """Grow a singleton organ if conditions met

        threshold = minimum strength we want to have AFTER creating the organ
        So we need: current_strength - creation_cost >= threshold
        """
        if organ_ref is not None:
            return organ_ref

        threshold = self.get_param(threshold_early)
        creation_cost = organ_class.CREATION_COST

        # Only grow if we'll have enough strength left after creation
        if self.strength() - creation_cost >= threshold and self.can_grow_organ():
            return organ_class(self)
        return None

    def grow_organs_adaptive(self):
        """Grow organs based on game phase and current state

        Priority order designed for survival:
        1. Type sensor (need to see)
        2. One cilia (need to move)
        3. PhotoGlands (need energy to survive)
        4. More cilia (mobility)
        5. Spikes (defense)
        6. Womb (reproduction)
        7. Other sensors/organs as energy allows
        """
        from shared import (
            Cilia,
            Cloaking,
            CreatureTypeSensor,
            EnergySensor,
            PhotoGland,
            PoisonGland,
            PoisonSensor,
            Spikes,
        )

        # PRIORITY 1: Type sensor - absolute must-have
        self.type_sensor = self.grow_singleton(1, self.type_sensor, CreatureTypeSensor)

        # PRIORITY 2: At least one cilia for movement
        cilia_threshold = self.get_param(0)
        if (
            len(self.cilia_list) == 0
            and self.strength() - Cilia.CREATION_COST >= cilia_threshold
            and self.can_grow_organ()
        ):
            self.cilia_list.append(Cilia(self))

        # PRIORITY 3: PhotoGlands for energy sustainability
        # PhotoGlands have negative maintenance (-150) so they're critical!
        target_photo = int(self.get_param(11))
        photo_threshold = self.get_param(5)
        while (
            self.photoglands < target_photo
            and self.strength() - PhotoGland.CREATION_COST >= photo_threshold
            and self.can_grow_organ()
        ):
            PhotoGland(self)
            self.photoglands += 1

        # PRIORITY 4: More cilia for mobility
        target_cilia = int(self.get_param(10))
        while (
            len(self.cilia_list) < target_cilia
            and self.strength() - Cilia.CREATION_COST >= cilia_threshold
            and self.can_grow_organ()
        ):
            self.cilia_list.append(Cilia(self))

        # PRIORITY 5: Spikes for defense
        self.spikes = self.grow_singleton(6, self.spikes, Spikes)

        # PRIORITY 6: Energy sensor for smart targeting
        self.energy_sensor = self.grow_singleton(2, self.energy_sensor, EnergySensor)

        # PRIORITY 7: Womb for reproduction
        self.womb = self.grow_singleton(8, self.womb, RLPropagator)

        # Late game organs (only if phase allows)
        phase = self.get_phase_weight()

        if phase > 0.3:
            self.poison_sensor = self.grow_singleton(
                4, self.poison_sensor, PoisonSensor
            )

        if phase > 0.5:
            self.poison_gland = self.grow_singleton(9, self.poison_gland, PoisonGland)

        # Cloaking is very expensive - only if lots of room
        if self.can_grow_organ() and self.count_organs() <= 6:
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

        # Safety check - need to be in a world
        try:
            if self.f_world() is None:
                return None, 0
        except:
            return None, 0

        best_score = -9999
        best_dir = None

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            # Enemy targeting
            if cell not in (Soil, Plant, DNA_CMA_ES_BUG_RED, None):
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
            DNA_CMA_ES_BUG_RED.reward_score += self.R_SUCCESS_REPRO

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
            if cell not in (Soil, Plant, None, DNA_CMA_ES_BUG_RED):
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
    #           TOP DNA MANAGEMENT FOR CMA-ES
    # ======================================================
    TOP_K = 10
    top_dna = []

    @classmethod
    def load_top_list(cls):
        if os.path.exists(cls.TOP_FILE):
            try:
                cls.top_dna = list(np.load(cls.TOP_FILE, allow_pickle=True))
            except:
                cls.top_dna = []
        else:
            cls.top_dna = []

    @classmethod
    def export_top_list(cls):
        entry = (cls.reward_score, np.copy(cls.DEFAULT_DNA))
        cls.top_dna.append(entry)
        cls.top_dna = sorted(cls.top_dna, key=lambda x: x[0], reverse=True)[: cls.TOP_K]
        np.save(cls.TOP_FILE, np.array(cls.top_dna, dtype=object))
        cls.reward_score = 0

    @classmethod
    def choose_initial_dna(cls):
        if cls.top_dna:
            return np.copy(cls.top_dna[0][1])
        return np.copy(cls.DEFAULT_DNA)


# ======================================================
#     Propagator - passes DNA to children
# ======================================================
class RLPropagator(Propagator):
    __slots__ = ()

    def make_child(self):
        return DNA_CMA_ES_BUG_RED(np.copy(self.host().dna))  # type: ignore
