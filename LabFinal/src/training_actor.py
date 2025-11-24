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

# =====================================================
#     DNA_CMA_ES_BUG_RED (ANTI-STAGNATION VERSION)
# =====================================================


class DNA_CMA_ES_BUG_RED(Creature):
    __instance_count = 0

    TOP_FILE = "dna_top10.npy"
    reward_score = 0
    colour = "#dd4444"

    # External (supplied from training loop)
    current_turn = 0
    turn_limit = 3000  # KILL MATCH after this many turns

    # ======================================================
    #                 REWARD CONSTANTS
    # ======================================================

    # Outcome - MASSIVELY increased win rewards
    R_WIN = +50000  # Winning is EVERYTHING
    R_LOSS = -20000
    R_TIMEOUT_DOMINATE = +15000  # Still good, but much worse than winning
    R_TIMEOUT_DRAW = -15000  # Massive punishment for draws

    # Combat - Increased rewards for aggression
    R_KILL = +200  # Much higher kill reward
    R_DEATH = -40  # Reduced death penalty (less risk-averse)
    R_DAMAGE_DEALT = +1.0  # 4x increase
    R_DAMAGE_TAKEN = -0.3  # Slightly increased
    R_AGGRESSION_BONUS = +50  # Much higher bonus for killing strong enemies

    # Reproduction
    R_SUCCESS_REPRO = +15
    R_USELESS_REPRO = -40

    # Poison
    R_POISON_HIT = +30
    R_POISON_WASTE = -10

    # Movement / activity - MUCH harsher passive penalties
    R_IDLE = -50  # Extreme punishment for not moving
    R_APPROACH_ENEMY = +20  # Double the approach reward
    R_RETREAT_ENEMY = -80  # MASSIVE punishment for retreating

    # Per turn - Reduced to minimal
    R_SURVIVE = +0.05  # Drastically reduced (was 0.50)
    R_TERRITORY = +0.10  # Drastically reduced (was 0.40)

    # ======================================================
    #              DNA CONFIG (20 values)
    # ======================================================
    DEFAULT_DNA = np.array(
        [
            100,
            150,
            200,
            180,
            200,
            300,
            250,
            500,
            400,
            600,  # organ thresholds
            1.0,
            0.7,
            1.0,
            0.01,  # movement weights
            0.4,
            1200,
            0.30,
            1000,
            0.10,
            0.35,  # behavior/tuning
        ],
        dtype=float,
    )

    def __init__(self, dna=None):
        super().__init__()
        DNA_CMA_ES_BUG_RED.__instance_count += 1
        self.dna = np.copy(dna) if dna is not None else np.copy(self.DEFAULT_DNA)

        self.cilia = None
        self.type_sensor = None
        self.energy_sensor = None
        self.life_sensor = None
        self.poison_sensor = None
        self.poison_gland = None
        self.cloak = None
        self.spikes = None
        self.womb = None

        self.photoglands = 0
        self.last_enemy_distance = None
        self.idle_turns = 0

    # ======================================================
    @classmethod
    def instance_count(cls):
        return DNA_CMA_ES_BUG_RED.__instance_count

    @classmethod
    def destroyed(cls):
        DNA_CMA_ES_BUG_RED.__instance_count -= 1

    # ======================================================
    #              HIGH-LEVEL MATCH REWARD
    # ======================================================

    @classmethod
    def reward_win(cls):
        cls.reward_score += cls.R_WIN

    @classmethod
    def reward_loss(cls):
        cls.reward_score += cls.R_LOSS

    @classmethod
    def reward_timeout(cls, my_count, opp_count):
        """Called at trainer end if turn_limit reached."""
        if my_count > opp_count:
            cls.reward_score += cls.R_TIMEOUT_DOMINATE
        elif my_count < opp_count:
            cls.reward_score -= cls.R_TIMEOUT_DOMINATE
        else:
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

        # Damage rewards
        dmg_to_enemy = max(0, def_before - def_after)
        dmg_to_me = max(0, my_before - my_after)

        DNA_CMA_ES_BUG_RED.reward_score += dmg_to_enemy * self.R_DAMAGE_DEALT
        DNA_CMA_ES_BUG_RED.reward_score += dmg_to_me * self.R_DAMAGE_TAKEN

        # BONUS: Reward for engaging in combat at all (NEW)
        if def_before > 0 and defender is not self:
            DNA_CMA_ES_BUG_RED.reward_score += 5  # Small bonus for any combat

        # Kill
        if result is self and def_before > 0:
            DNA_CMA_ES_BUG_RED.reward_score += self.R_KILL

            # Scale aggression bonus by enemy strength
            if def_before > 500:
                DNA_CMA_ES_BUG_RED.reward_score += self.R_AGGRESSION_BONUS * (
                    def_before / 500
                )

        # Suicide attack = bad (but not catastrophic)
        if result is defender and defender is not self:
            DNA_CMA_ES_BUG_RED.reward_score -= 30  # Reduced penalty

        return result

    # ======================================================
    #                       TURN
    # ======================================================
    def do_turn(self):
        # Turn limit check — hyper-aggressive
        if DNA_CMA_ES_BUG_RED.current_turn >= DNA_CMA_ES_BUG_RED.turn_limit:
            return  # trainer finalizes reward

        DNA_CMA_ES_BUG_RED.reward_score += self.R_SURVIVE

        if self.f_apparent_type() is DNA_CMA_ES_BUG_RED:
            DNA_CMA_ES_BUG_RED.reward_score += self.R_TERRITORY

        old_pos = self.f_location()

        self.maybe_grow_organs()
        self.maybe_cloak()
        self.maybe_poison_drop()
        self.maybe_reproduce()
        self.act_move()

        # Idle detection
        if self.f_location() == old_pos:
            self.idle_turns += 1
            DNA_CMA_ES_BUG_RED.reward_score += self.R_IDLE
            if self.idle_turns >= 3:  # ultra-aggressive penalty
                DNA_CMA_ES_BUG_RED.reward_score -= 50
        else:
            self.idle_turns = 0

    # ======================================================
    #                     ORGAN GROWTH
    # ======================================================
    def maybe_grow(self, threshold, organ_obj, cls):
        if organ_obj is None and self.strength() > threshold:
            return cls(self)
        return organ_obj

    def maybe_grow_photogland(self, threshold):
        if self.strength() > threshold:
            PhotoGland(self)
            self.photoglands += 1

    def maybe_grow_organs(self):
        d = self.dna
        self.cilia = self.maybe_grow(d[0], self.cilia, Cilia)
        self.type_sensor = self.maybe_grow(d[1], self.type_sensor, CreatureTypeSensor)
        self.energy_sensor = self.maybe_grow(d[2], self.energy_sensor, EnergySensor)
        self.life_sensor = self.maybe_grow(d[3], self.life_sensor, LifeSensor)
        self.poison_sensor = self.maybe_grow(d[4], self.poison_sensor, PoisonSensor)

        self.maybe_grow_photogland(d[5])
        self.spikes = self.maybe_grow(d[6], self.spikes, Spikes)
        self.cloak = self.maybe_grow(d[7], self.cloak, Cloaking)
        self.womb = self.maybe_grow(d[8], self.womb, RLPropagator)
        self.poison_gland = self.maybe_grow(d[9], self.poison_gland, PoisonGland)

    # ======================================================
    #                       CLOAK
    # ======================================================
    def maybe_cloak(self):
        if self.cloak is None:
            return
        strength_frac = self.strength() / Creature.MAX_STRENGTH
        if strength_frac < self.dna[19]:
            self.cloak.cloak()
        else:
            self.cloak.uncloak()

    # ======================================================
    #                  POISON
    # ======================================================
    def maybe_poison_drop(self):
        if self.poison_gland is None:
            return
        if self.strength() < self.dna[17]:
            return

        has_target = False
        if self.type_sensor:
            for d in Direction:
                cell = self.type_sensor.sense(d)
                if cell not in (Soil, Plant, None, DNA_CMA_ES_BUG_RED):
                    has_target = True
                    break

        direction = random.choice(list(Direction))
        self.poison_gland.drop_poison(direction, 20)

        DNA_CMA_ES_BUG_RED.reward_score += (
            self.R_POISON_HIT if has_target else self.R_POISON_WASTE
        )

    # ======================================================
    #                 REPRODUCTION
    # ======================================================
    def maybe_reproduce(self):
        if self.womb is None:
            return
        if self.strength() <= self.dna[15]:
            return

        before = self.instance_count()
        give = int(self.strength() * self.dna[16])
        self.womb.give_birth(give, Direction.random())
        after = self.instance_count()

        if after > before:
            DNA_CMA_ES_BUG_RED.reward_score += self.R_SUCCESS_REPRO
        else:
            DNA_CMA_ES_BUG_RED.reward_score += self.R_USELESS_REPRO

    # ======================================================
    #             MOVEMENT (Hyper-Aggressive)
    # ======================================================
    def enemy_distance(self):
        """Returns distance to nearest visible enemy."""
        if self.type_sensor is None:
            return None
        best = None
        for d in Direction:
            t = self.type_sensor.sense(d)
            if t not in (Soil, Plant, DNA_CMA_ES_BUG_RED):
                return 1  # adjacent enemy found
        return 5  # no nearby enemies → coarse distance

    def act_move(self):
        if self.cilia is None:
            return

        # No sensors? Random but biased aggressive
        if self.type_sensor is None:
            if random.random() < 0.8:
                self.cilia.move_in_direction(Direction.random())
            return

        # Evaluate movement
        d = self.dna
        best_score = -9999
        best_dir = None

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            # Seek combat
            if cell is Plant:
                score += d[10]
            elif cell not in (Soil, DNA_CMA_ES_BUG_RED):
                score += d[11] * 4.0  # MUCH more aggressive

            # Avoid poison
            if self.poison_sensor and self.poison_sensor.sense(direction):
                score -= d[12]

            # Consider energy
            if self.energy_sensor:
                score += self.energy_sensor.sense(direction) * d[13]

            if score > best_score:
                best_score = score
                best_dir = direction

        # Move
        if best_score > d[14]:
            self.cilia.move_in_direction(best_dir)  # type: ignore
        else:
            # Force forward aggression sometimes
            if random.random() < 0.6:
                self.cilia.move_in_direction(Direction.random())

        # Aggression pressure reward
        new_dist = self.enemy_distance()
        if new_dist is not None:
            if self.last_enemy_distance is None:
                self.last_enemy_distance = new_dist
            else:
                if new_dist < self.last_enemy_distance:
                    DNA_CMA_ES_BUG_RED.reward_score += self.R_APPROACH_ENEMY
                elif new_dist > self.last_enemy_distance:
                    DNA_CMA_ES_BUG_RED.reward_score += self.R_RETREAT_ENEMY

            self.last_enemy_distance = new_dist

    # ======================================================
    #           TOP DNA MANAGEMENT FOR CMA-ES
    # ======================================================
    TOP_K = 10
    top_dna = []

    @classmethod
    def load_top_list(cls):
        if os.path.exists(cls.TOP_FILE):
            cls.top_dna = list(np.load(cls.TOP_FILE, allow_pickle=True))
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
#     Propagator (no mutation)
# ======================================================


class RLPropagator(Propagator):
    __slots__ = ()

    def make_child(self):
        return DNA_CMA_ES_BUG_RED(np.copy(self.host().dna))  # type: ignore
