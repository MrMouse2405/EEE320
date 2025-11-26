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
#     TURTLE (Read-Only)
# =====================================================


class TURTLE(Creature):
    """
    Inference-only version of the trained bug.
    Loads best DNA from training and uses it without any reward scoring.
    """

    __instance_count = 0

    # Load from the training file
    TOP_FILE = "dna_top10.npy"
    colour = "#4444dd"  # Blue to distinguish from training red

    # Default DNA (fallback if no trained weights exist)
    DEFAULT_DNA = np.array(
        [
            99.89944278302376,
            150.08321282398228,
            200.25182166442735,
            251.2231517440338,
            199.48071052578427,
            300.71026394755063,
            250.21073329095108,
            798.9100918242272,
            398.4206542911472,
            599.4549753587369,
            1.444299320607352,
            3.6152115509537586,
            0.6572991092268756,
            -0.3435177880185379,
            1.4771936255091704,
            -0.014561049386003444,
            -0.40933999667512344,
            1.4087078655106906,
            1.1602187984348573,
            1.2899622329201264,
            -1.2165623736652216,
            0.8083254616869997,
            0.5686417454946018,
            1.0174552577666585,
            800.2916020682258,
            -0.75395751522009,
            0.64181163068631,
            1199.6599266530457,
            0.8800346961931608,
            1.499107616199532,
            1.3594384158420927,
            -1.1303458092100778,
        ],
        dtype=float,
    )

    def __init__(self, dna=None):
        super().__init__()
        TURTLE.__instance_count += 1

        # Use provided DNA or load best from file
        if dna is not None:
            self.dna = np.copy(dna)
        else:
            self.dna = self.load_best_dna()

        # Organs
        self.cilia_count = 0
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
        self.last_enemy_distance = None
        self.idle_turns = 0
        self.offspring_count = 0
        self.moves_this_turn = 0

    # ======================================================
    @classmethod
    def instance_count(cls):
        return TURTLE.__instance_count

    @classmethod
    def destroyed(cls):
        TURTLE.__instance_count -= 1

    # ======================================================
    #              LOAD BEST DNA
    # ======================================================
    @classmethod
    def load_best_dna(cls):
        """Load the best DNA from training file."""
        # if os.path.exists(cls.TOP_FILE):
        #     try:
        #         top_dna_list = list(np.load(cls.TOP_FILE, allow_pickle=True))
        #         if len(top_dna_list) > 0:
        #             # Get the best DNA (highest reward)
        #             best_entry = top_dna_list[0]
        #             best_dna = best_entry[1]
        #             print(f"[INFERENCE] Loaded best DNA with reward: {best_entry[0]}")
        #             return np.copy(best_dna)
        #     except Exception as e:
        #         print(f"[INFERENCE] Failed to load DNA: {e}")

        # print("[INFERENCE] No trained DNA found, using default")
        return np.copy(cls.DEFAULT_DNA)

    # ======================================================
    #                       TURN
    # ======================================================
    def do_turn(self):
        """Execute turn without any reward scoring."""
        old_pos = self.f_location()
        self.moves_this_turn = 0

        # Grow organs
        self.maybe_grow_organs()

        # === DNA-DRIVEN ACTION PRIORITIZATION ===
        actions = [
            (self.dna[13], self.act_move_combat),
            (self.dna[14], self.maybe_reproduce),
            (self.dna[15], self.maybe_poison_drop),
            (self.dna[16], self.maybe_cloak),
        ]

        # Sort by priority
        actions.sort(key=lambda x: x[0], reverse=True)

        # Execute actions
        for priority, action in actions:
            if priority > 0.05:
                action()

        # Track idle turns
        if self.f_location() == old_pos:
            self.idle_turns += 1
        else:
            self.idle_turns = 0

    # ======================================================
    #                     ORGAN GROWTH
    # ======================================================
    def count_organs(self):
        """Count total organs."""
        count = self.photoglands + self.cilia_count
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

    def maybe_grow_singleton(self, threshold, organ_obj, cls):
        """Grow singleton organs."""
        if organ_obj is None and self.strength() > threshold:
            if self.count_organs() < Creature.MAX_ORGANS:
                return cls(self)
        return organ_obj

    def maybe_grow_organs(self):
        d = self.dna

        # Essential organs
        self.type_sensor = self.maybe_grow_singleton(
            d[1], self.type_sensor, CreatureTypeSensor
        )
        self.spikes = self.maybe_grow_singleton(d[6], self.spikes, Spikes)

        # Multiple cilia for movement
        target_cilia = int(d[10])
        while (
            self.cilia_count < target_cilia
            and self.strength() > d[0]
            and self.count_organs() < Creature.MAX_ORGANS
        ):
            Cilia(self)
            self.cilia_count += 1

        # Secondary sensors
        self.energy_sensor = self.maybe_grow_singleton(
            d[2], self.energy_sensor, EnergySensor
        )
        self.poison_sensor = self.maybe_grow_singleton(
            d[4], self.poison_sensor, PoisonSensor
        )

        # Photoglands
        target_photoglands = int(d[11])
        while (
            self.photoglands < target_photoglands
            and self.strength() > d[5]
            and self.count_organs() < Creature.MAX_ORGANS
        ):
            PhotoGland(self)
            self.photoglands += 1

        # Strategic organs
        self.womb = self.maybe_grow_singleton(d[8], self.womb, InferencePropagator)
        self.poison_gland = self.maybe_grow_singleton(
            d[9], self.poison_gland, PoisonGland
        )

        # Expensive organs
        self.cloak = self.maybe_grow_singleton(d[7], self.cloak, Cloaking)
        self.life_sensor = self.maybe_grow_singleton(d[3], self.life_sensor, LifeSensor)

    # ======================================================
    #                       CLOAK
    # ======================================================
    def maybe_cloak(self):
        if self.cloak is None:
            return

        strength_frac = self.strength() / Creature.MAX_STRENGTH

        if strength_frac < self.dna[25]:
            self.cloak.cloak()
        else:
            self.cloak.uncloak()

    # ======================================================
    #                  POISON
    # ======================================================
    def maybe_poison_drop(self):
        if self.poison_gland is None or self.type_sensor is None:
            return

        if self.strength() < 800:
            return

        # Check for adjacent enemies
        adjacent_enemy = False
        enemy_direction = None

        for d in Direction:
            cell = self.type_sensor.sense(d)
            if cell not in (Soil, Plant, None, TURTLE):
                adjacent_enemy = True
                enemy_direction = d
                break

        if adjacent_enemy and random.random() < self.dna[31]:
            self.poison_gland.drop_poison(enemy_direction, 30)
        elif not adjacent_enemy and random.random() < 0.05:
            self.poison_gland.drop_poison(Direction.random(), 20)

    # ======================================================
    #                 REPRODUCTION
    # ======================================================
    def maybe_reproduce(self):
        if self.womb is None:
            return

        if self.offspring_count >= int(self.dna[29]):
            return

        if self.strength() <= self.dna[27]:
            return

        pop = self.instance_count()
        if pop > 5 and self.strength() < self.dna[27] * self.dna[30]:
            return

        before = self.instance_count()
        give = int(self.strength() * self.dna[28])
        self.womb.give_birth(give, Direction.random())
        after = self.instance_count()

        if after > before:
            self.offspring_count += 1

    # ======================================================
    #             MOVEMENT & COMBAT
    # ======================================================
    def find_best_target(self):
        """Find the most valuable direction to move."""
        if self.type_sensor is None:
            return None, None, 0

        best_score = -9999
        best_dir = None
        best_type = None

        d = self.dna

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            # Target enemies
            if cell not in (Soil, Plant, TURTLE, None):
                enemy_strength = 0
                if self.energy_sensor:
                    enemy_strength = self.energy_sensor.sense(direction)

                strength_ratio = self.strength() / max(enemy_strength, 1)

                if strength_ratio >= d[23] and self.strength() >= d[24]:
                    score += d[18] * 100

                    if strength_ratio >= d[26]:
                        score += 200
                else:
                    score -= 100

            # Plants
            elif cell is Plant:
                score += d[19] * 10

            # Avoid poison
            if self.poison_sensor and self.poison_sensor.sense(direction):
                score += d[20] * 10

            # Energy consideration
            if self.energy_sensor:
                energy = self.energy_sensor.sense(direction)
                score += energy * d[21]

            if score > best_score:
                best_score = score
                best_dir = direction
                best_type = cell

        return best_dir, best_type, best_score

    def use_one_cilia(self, direction):
        """Use one cilia to move."""
        if self.cilia_count <= 0:
            return False

        cilia = Cilia(self)
        self.cilia_count -= 1
        cilia.move_in_direction(direction)
        self.moves_this_turn += 1
        return True

    def act_move_combat(self):
        """Movement and combat logic."""
        if self.cilia_count <= 0:
            return

        # Calculate enemy distance
        enemy_dist = None
        if self.type_sensor:
            for d in Direction:
                t = self.type_sensor.sense(d)
                if t not in (Soil, Plant, TURTLE, None):
                    enemy_dist = 1
                    break
            if enemy_dist is None:
                enemy_dist = 5

        # Determine moves
        max_moves = min(self.cilia_count, 3)

        if enemy_dist and enemy_dist <= 2:
            max_moves = min(self.cilia_count, 5)

        # Make moves
        moves_made = 0

        for _ in range(max_moves):
            if self.cilia_count <= 0:
                break

            best_dir, best_type, best_score = self.find_best_target()

            if best_dir is None:
                if random.random() < 0.7:
                    self.use_one_cilia(Direction.random())
                    moves_made += 1
                break

            if best_score < -50:
                break

            if random.random() < self.dna[22]:
                if self.use_one_cilia(best_dir):
                    moves_made += 1

                    if best_type not in (Soil, Plant, TURTLE, None):
                        break
            else:
                break

        # Update distance tracking
        if enemy_dist is not None:
            self.last_enemy_distance = enemy_dist


# ======================================================
#     Propagator (no mutation)
# ======================================================


class InferencePropagator(Propagator):
    __slots__ = ()

    def make_child(self):
        return TURTLE(np.copy(self.host().dna))  # type: ignore
