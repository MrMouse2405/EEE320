"""
DNA_CMA_ES_BUG_INFERENCE3

Phase-Based Adaptive Strategy. Inference File

Competition-ready version


"""

import random

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

"""

    Weights

"""

"""
DNA_3
Auto-generated DNA weights from training.
Best reward: 63,907,270
DNA length: 64
"""

# Best trained DNA as plain Python list
TRAINED_DNA = [
    198.94544695167343,
    100.34810664672571,
    297.66789251493685,
    801.4660843731707,
    599.5317282739293,
    347.8687769739553,
    248.41558350841413,
    1199.9958939836604,
    299.2296184756335,
    998.5687821657561,
    2.9809456875002756,
    3.2756925163515525,
    2.307025848576478,
    0.8211544969232868,
    0.39909374314128887,
    0.4848243094357476,
    0.23259741843753612,
    0.6529782780196932,
    2.05627501764576,
    5.627712447730035,
    -0.9675405829589723,
    0.0791958050876967,
    0.3545470239991675,
    1.3251897223336726,
    500.9000217747613,
    0.2116335426097764,
    0.993381341835375,
    799.5320256562622,
    0.302531870523222,
    2.590827642160911,
    0.10172912804851475,
    0.2028214748515058,
    149.61186761770915,
    100.72474680410119,
    198.6431348918811,
    502.7453651658838,
    400.3158849646327,
    299.1314505372161,
    200.42624462375255,
    497.6837384061062,
    250.54427357186495,
    599.8109459965194,
    5.1358752245329455,
    1.6349702287805776,
    1.8043690772079066,
    0.5725355182553097,
    0.9772291995703257,
    0.986978503251234,
    0.26833972006333673,
    0.4246584635092411,
    2.6261803381949553,
    1.128990278356842,
    -0.48721010231531053,
    0.09810789406110267,
    0.5781302458957669,
    0.9635570668827071,
    349.9342203740288,
    0.14671569604611753,
    1.8188816276074036,
    999.4003067355901,
    0.2746812465870101,
    4.970427105794644,
    0.2278743050711829,
    0.67164091786061,
]

"""

    Inference Engine

"""


class DNA_CMA_ES_BUG_INFERENCE3(Creature):
    """
    Inference-only version of the phase-based trained bug.
    Uses plain Python lists - no numpy required.
    """

    __instance_count = 0
    colour = "#4444dd"

    # Phase transition (number of turns for full transition from early to late game)
    PHASE_TRANSITION = 500

    def __init__(self, dna=None):
        super().__init__()
        DNA_CMA_ES_BUG_INFERENCE3.__instance_count += 1

        # Use provided DNA or class default
        if dna is not None:
            self.dna = list(dna)  # Copy as plain list
        else:
            self.dna = list(TRAINED_DNA)

        # Organs - store actual references for cilia
        self.cilia_list = []
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

    # ==========================================================================
    #              INSTANCE COUNTING
    # ==========================================================================
    @classmethod
    def instance_count(cls):
        return DNA_CMA_ES_BUG_INFERENCE3.__instance_count

    @classmethod
    def destroyed(cls):
        DNA_CMA_ES_BUG_INFERENCE3.__instance_count -= 1

    # ==========================================================================
    #              PHASE-BASED DNA ACCESS
    # ==========================================================================
    def get_phase_weight(self):
        """Returns interpolation weight: 0 = early game, 1 = late game.

        Uses bug's age as proxy for game phase.
        """
        if self.age <= 0:
            return 0.0
        elif self.age >= self.PHASE_TRANSITION:
            return 1.0
        else:
            return self.age / self.PHASE_TRANSITION

    def get_param(self, early_idx, late_idx=None):
        """Get parameter interpolated between early and late game."""
        if late_idx is None:
            late_idx = early_idx + 32

        phase = self.get_phase_weight()
        early_val = self.dna[early_idx]
        late_val = self.dna[late_idx]
        return early_val + phase * (late_val - early_val)

    # ==========================================================================
    #                       TURN
    # ==========================================================================
    def do_turn(self):
        """Execute turn."""
        self.age += 1

        # Grow organs based on phase
        self.grow_organs_adaptive()

        # Execute actions based on phase-weighted priorities
        self.execute_actions()

    # ==========================================================================
    #                  ORGAN MANAGEMENT
    # ==========================================================================
    def count_organs(self):
        """Count total organs."""
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
        """Grow a singleton organ if conditions met."""
        if organ_ref is not None:
            return organ_ref

        threshold = self.get_param(threshold_early)
        creation_cost = organ_class.CREATION_COST

        if self.strength() - creation_cost >= threshold and self.can_grow_organ():
            return organ_class(self)
        return None

    def grow_organs_adaptive(self):
        """Grow organs based on game phase and current state."""

        # ALWAYS prioritize type sensor (need to see enemies)
        self.type_sensor = self.grow_singleton(1, self.type_sensor, CreatureTypeSensor)

        # Spikes for defense
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

        if phase > 0.3:
            self.poison_sensor = self.grow_singleton(
                4, self.poison_sensor, PoisonSensor
            )

        if phase > 0.4:
            self.poison_gland = self.grow_singleton(9, self.poison_gland, PoisonGland)

        if self.can_grow_organ() and self.count_organs() <= 7:
            self.cloak = self.grow_singleton(7, self.cloak, Cloaking)

    # ==========================================================================
    #                  ACTION EXECUTION
    # ==========================================================================
    def execute_actions(self):
        """Execute actions based on weighted priorities."""
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

        # Sort by weight (highest first)
        actions.sort(key=lambda x: x[0], reverse=True)

        # Execute all actions with weight > 0.05
        for weight, action in actions:
            if weight > 0.05:
                action()

    # ==========================================================================
    #                  COMBAT / MOVEMENT
    # ==========================================================================
    def get_available_cilia(self):
        """Get cilia that haven't been used this turn."""
        return [c for c in self.cilia_list if c.f_uses_this_turn() == 0]

    def act_combat(self):
        """Main combat/movement action."""
        available = self.get_available_cilia()
        if not available:
            return

        move_prob = self.get_param(22)
        enemy_attraction = self.get_param(18)
        plant_attraction = self.get_param(19)
        poison_avoidance = self.get_param(20)
        min_ratio = self.get_param(23)
        min_strength = self.get_param(24)

        # Determine number of moves to make (2-6 based on phase)
        phase = self.get_phase_weight()
        max_moves = min(len(available), int(2 + phase * 4))

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
        """Evaluate all 8 directions and return best one."""
        if self.type_sensor is None:
            return None, 0

        best_score = -9999
        best_dir = None

        for direction in Direction:
            score = 0.0
            cell = self.type_sensor.sense(direction)

            # Enemy targeting
            if cell not in (Soil, Plant, DNA_CMA_ES_BUG_INFERENCE3, None):
                enemy_strength = 0
                if self.energy_sensor:
                    enemy_strength = self.energy_sensor.sense(direction)

                my_strength = self.strength()
                strength_ratio = my_strength / max(enemy_strength, 1)

                if strength_ratio >= min_ratio and my_strength >= min_strength:
                    score += enemy_attraction * 100
                    if strength_ratio >= 2.0:
                        score += 150  # Easy kill bonus
                else:
                    score -= 150

            # Plant attraction (food)
            elif cell is Plant:
                score += plant_attraction * 20

            # Poison avoidance
            if self.poison_sensor and self.poison_sensor.sense(direction):
                score += poison_avoidance * 30

            # Energy bonus for plant targets
            if self.energy_sensor and cell is Plant:
                energy = self.energy_sensor.sense(direction)
                score += energy * 0.01

            if score > best_score:
                best_score = score
                best_dir = direction

        return best_dir, best_score

    # ==========================================================================
    #                  REPRODUCTION
    # ==========================================================================
    def act_reproduce(self):
        """Attempt to reproduce."""
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

        # Population check
        pop = self.instance_count()
        pop_scale = self.get_param(30)
        if pop > 10 and self.strength() < min_strength * (1 + pop * pop_scale * 0.01):
            return

        # Find direction for birth
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

    # ==========================================================================
    #                  POISON
    # ==========================================================================
    def act_poison(self):
        """Use poison gland if appropriate."""
        if self.poison_gland is None or self.type_sensor is None:
            return

        if self.strength() < 600:
            return

        # Look for adjacent enemies
        for d in Direction:
            cell = self.type_sensor.sense(d)
            if cell not in (Soil, Plant, None, DNA_CMA_ES_BUG_INFERENCE3):
                if random.random() < 0.5:
                    self.poison_gland.drop_poison(d, 25)
                return

    # ==========================================================================
    #                  CLOAK
    # ==========================================================================
    def act_cloak(self):
        """Manage cloaking based on strength."""
        if self.cloak is None:
            return

        cloak_threshold = self.get_param(25)
        strength_frac = self.strength() / Creature.MAX_STRENGTH

        if strength_frac < cloak_threshold:
            self.cloak.cloak()
        else:
            self.cloak.uncloak()


# ==========================================================================
#     Propagator - passes DNA to children
# ==========================================================================
class InferencePropagator(Propagator):
    """Propagator that creates children with same DNA."""

    def make_child(self):
        # Copy DNA as plain list
        parent_dna = list(self.host().dna)
        return DNA_CMA_ES_BUG_INFERENCE3(parent_dna)
