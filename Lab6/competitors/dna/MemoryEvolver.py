"""
MemoryEvolver: DNA-driven adaptive species (hardened + documented)

What’s new (vs. vanilla MemoryEvolver):
- Stochastic control:
  * Elitism: occasionally clone without mutation when quality is high.
  * Adaptive mutation temperature: scale mutation intensity by recent fitness.
- In-life learning:
  * Small bandit-like nudges to behavior weights within an individual's lifespan.
  * Soft inheritance: learned weights bias the child's genome during mutation.
- Sensor robustness:
  * Priority organ growth (Cilia -> TypeSensor -> 1 PhotoGland -> Womb).
  * Fallback heuristics when sensors are missing.
  * Biased random walk with last-direction memory.
- Performance:
  * __slots__, tuple/constant caching, single sensor reads per direction.
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

# --- micro-optimized aliases for hot paths ---
DIRECTIONS = tuple(Direction)
_rand = random.random
_gauss = random.gauss
_choice = random.choice
_uniform = random.uniform
_randint = random.randint


def _clamp(x: float, lo: float, hi: float) -> float:
    """Cheap clamp that avoids extra branches."""
    return hi if x > hi else lo if x < lo else x


class MemoryEvolver(Creature):
    """
    DNA layout (index-based for speed/memory):
      organs      = [cilia, type_sensor, energy_sensor, life_sensor, poison_sensor, photo_count, cloak, spikes, womb]
      weights     = [prefer_plant, prefer_enemy, avoid_poison, energy_seek_scale]
      thresholds  = [move_score, repro_strength_frac, repro_give_frac, weak_cloak_frac]
      flags       = [cloak_when_weak, random_walk_if_stalled]
      mutation    = [weight_sigma, thresh_sigma, flip_flag_prob, toggle_organs_prob, max_photo, max_spikes, max_cilia]
    """

    __slots__ = (
        # DNA
        "dna_organs",
        "dna_weights",
        "dna_thresholds",
        "dna_flags",
        "dna_mutation",
        # Organs (lazy-grown)
        "cilia",
        "type_sensor",
        "energy_sensor",
        "life_sensor",
        "poison_sensor",
        "womb",
        "cloak",
        "spikes",
        "photoglands",
        # Learning + quality tracking
        "_learned_weights",
        "_learn_rate",
        "fit_food_gain",
        "fit_kills",
        "fit_losses",
        # Misc state
        "lineage_jitter",
        "last_dir",
    )

    __instance_count = 0
    colour = "#4444dd"

    # Default DNA (tuples shared across instances; copied to lists on init)
    DEFAULT_ORGANS = (1, 1, 1, 1, 1, 1, 0, 0, 1)
    DEFAULT_WEIGHTS = (1.2, 0.8, 1.5, 0.002)
    DEFAULT_THRESHOLDS = (0.6, 0.70, 0.40, 0.25)
    DEFAULT_FLAGS = (False, True)
    DEFAULT_MUTATION = (0.15, 0.08, 0.06, 0.03, 2, 1, 1)

    # --------- framework hooks ----------
    @classmethod
    def instance_count(cls):
        return MemoryEvolver.__instance_count

    @classmethod
    def destroyed(cls):
        MemoryEvolver.__instance_count -= 1

    # ------------- lifecycle -------------
    def __init__(self, dna: Tuple | None = None):
        super().__init__()
        MemoryEvolver.__instance_count += 1

        # DNA materialized to per-instance lists
        if dna is None:
            self.dna_organs = list(self.DEFAULT_ORGANS)
            self.dna_weights = list(self.DEFAULT_WEIGHTS)
            self.dna_thresholds = list(self.DEFAULT_THRESHOLDS)
            self.dna_flags = list(self.DEFAULT_FLAGS)
            self.dna_mutation = list(self.DEFAULT_MUTATION)
        else:
            (
                self.dna_organs,
                self.dna_weights,
                self.dna_thresholds,
                self.dna_flags,
                self.dna_mutation,
            ) = dna

        # Organs (lazy)
        self.cilia = self.type_sensor = self.energy_sensor = None
        self.life_sensor = self.poison_sensor = None
        self.womb = self.cloak = self.spikes = None
        self.photoglands = 0

        # In-life plasticity: learned weights track small adjustments
        self._learned_weights = list(self.dna_weights)
        self._learn_rate = 0.02  # conservative to keep behavior stable

        # Rolling performance (decayed averages)
        self.fit_food_gain = 0.0
        self.fit_kills = 0.0
        self.fit_losses = 0.0

        # Tiny lineage bias to avoid perfect ties within identical DNA
        self.lineage_jitter = _uniform(-0.05, 0.05)

        # Navigation memory for biased random walk fallback
        self.last_dir = None

    # ------------- main turn -------------
    def do_turn(self):
        self._grow_organs_priority()  # ensure we've got the survival set first
        self._grow_organs_rest()  # then fill in remaining DNA desires
        self._maybe_cloak()
        self._maybe_reproduce()
        self._act()

    # ---------- organ growth: priority set ----------
    def _grow_organs_priority(self):
        """
        Priority: Cilia -> TypeSensor -> 1 PhotoGland -> Womb.
        Early returns keep spending focused; ensures basic viability even if DNA toggles are hostile.
        """

        def can_afford(cost: int) -> bool:
            return self.strength() > cost + 10

        # Movement first
        if (
            self.cilia is None
            and self.dna_organs[0]
            and can_afford(Cilia.CREATION_COST)
        ):
            self.cilia = Cilia(self)
            return

        # Perception (type) next
        if (
            self.type_sensor is None
            and self.dna_organs[1]
            and can_afford(CreatureTypeSensor.CREATION_COST)
        ):
            self.type_sensor = CreatureTypeSensor(self)
            return

        # Baseline energy income
        if self.photoglands < 1 and can_afford(PhotoGland.CREATION_COST):
            PhotoGland(self)
            self.photoglands = 1
            return

        # Reproduction capability
        if (
            self.womb is None
            and self.dna_organs[8]
            and can_afford(Propagator.CREATION_COST)
        ):
            self.womb = MemoryEvoPropagator(self)
            return

    # ---------- organ growth: rest of plan ----------
    def _grow_organs_rest(self):
        def can_afford(cost: int) -> bool:
            return self.strength() > cost + 10

        o = self.dna_organs

        # Remaining sensors
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

        # Additional photosynthesis (bounded by DNA photo_count)
        while self.photoglands < o[5] and can_afford(PhotoGland.CREATION_COST):
            PhotoGland(self)
            self.photoglands += 1

        # Defense / stealth
        if o[7] and self.spikes is None and can_afford(Spikes.CREATION_COST):
            self.spikes = Spikes(self)
        if o[6] and self.cloak is None and can_afford(Cloaking.CREATION_COST):
            self.cloak = Cloaking(self)

        # Womb if missed earlier (e.g., DNA off then on)
        if o[8] and self.womb is None and can_afford(Propagator.CREATION_COST):
            self.womb = MemoryEvoPropagator(self)

    # ------------- cloak logic -------------
    def _maybe_cloak(self):
        # flags[0] = cloak_when_weak ; thresholds[3] = weak_cloak_frac
        if not (self.cloak and self.dna_flags[0]):
            return
        weak_gate = self.dna_thresholds[3] * Creature.MAX_STRENGTH
        if self.strength() < weak_gate:
            self.cloak.cloak()  # use-cost paid internally; death handled by framework
        else:
            self.cloak.uncloak()  # stop paying cloak's extra maintenance

    # ------------- reproduction -------------
    def _maybe_reproduce(self):
        if not self.womb:
            return

        strength = self.strength()
        # thresholds[1] = repro_strength_frac, [2] = repro_give_frac
        if strength >= self.dna_thresholds[1] * Creature.MAX_STRENGTH:
            give = max(
                Propagator.CREATION_COST + 5, int(strength * self.dna_thresholds[2])
            )

            # Compute quality from rolling signals: more kills/food, fewer losses
            quality = (self.fit_kills + 0.5 * self.fit_food_gain) - (
                1.2 * self.fit_losses
            )

            # Elitism: clone probability rises with quality (cap to a small band)
            clone_prob = 0.2 + _clamp(0.1 * quality, 0.0, 0.2)
            do_clone = _rand() < clone_prob

            # Mutation temperature: >1 = wilder mutations when doing poorly
            if quality > 0.5:
                temp = 0.7
            elif quality < -0.5:
                temp = 1.4
            else:
                temp = 1.0

            # Prefer Soil/Plant nursery spots if we can sense them
            d = None
            if self.type_sensor:
                for dir_ in DIRECTIONS:
                    t = self.type_sensor.sense(dir_)
                    if t is Soil or t is Plant:
                        d = dir_
                        break
            if d is None:
                d = _choice(DIRECTIONS)

            # Inform propagator of mutation temperature & elitism choice
            if hasattr(self.womb, "set_temp"):
                self.womb.set_temp(temp, do_clone, self._learned_weights)

            self.womb.give_birth(give, d)

    # ------------- behavior / action -------------
    def _act(self):
        # Need at least movement + some notion of what's ahead
        if not self.cilia:
            return

        # Blend genome weights with learned weights for mild in-life adaptation
        w = self.dna_weights
        lw = self._learned_weights
        use_w = (
            0.8 * w[0] + 0.2 * lw[0],  # prefer_plant
            0.8 * w[1] + 0.2 * lw[1],  # prefer_enemy
            0.8 * w[2] + 0.2 * lw[2],  # avoid_poison
            0.8 * w[3] + 0.2 * lw[3],  # energy_seek_scale
        )

        base_move_th = self.dna_thresholds[0]
        # If missing PoisonSensor, be extra cautious
        move_threshold = base_move_th + (0.2 if self.poison_sensor is None else 0.0)

        has_type = self.type_sensor is not None
        has_life = self.life_sensor is not None
        has_poison = self.poison_sensor is not None
        has_energy = self.energy_sensor is not None
        jitter = self.lineage_jitter

        best_d = None
        best_score = float("-inf")

        pre_strength = self.strength()  # for reward estimation

        # Score each direction once with available sensors
        for d in DIRECTIONS:
            score = 0.0

            if has_type:
                tval = self.type_sensor.sense(d)
                if tval is Plant:
                    score += use_w[0]
                elif (tval is not Soil) and (tval is not MemoryEvolver):
                    score += use_w[1]
            elif has_life:
                # Coarse fallback: prefer "something is there" a bit (could be plant/enemy)
                if self.life_sensor.sense(d):
                    score += 0.5 * use_w[0]

            if has_poison and self.poison_sensor.sense(d):
                score -= use_w[2]

            if has_energy:
                score += self.energy_sensor.sense(d) * use_w[3]

            score += jitter

            if score > best_score:
                best_score = score
                best_d = d

        acted = False
        # Commit if confident
        if best_d and best_score >= move_threshold:
            self.cilia.move_in_direction(best_d)
            self.last_dir = best_d
            acted = True
        else:
            # Exploration fallback (biased random walk, avoid 180 turns)
            if self.dna_flags[1] and _rand() < 0.25:
                if self.last_dir and _rand() < 0.7:
                    idx = DIRECTIONS.index(self.last_dir)
                    next_dir = DIRECTIONS[(idx + _choice((-1, 0, 1))) % len(DIRECTIONS)]
                else:
                    next_dir = _choice(DIRECTIONS)
                self.cilia.move_in_direction(next_dir)
                self.last_dir = next_dir
                acted = True

        # --------- in-life learning & fitness tracking ----------
        post_strength = self.strength()
        delta = post_strength - pre_strength

        # Reward: normalize into [-1, 1] (very rough but stable)
        # Positive if we fed or won; negative if we lost big
        reward = _clamp(delta / 200.0, -1.0, 1.0)

        # If we acted and did not lose much, a slight positive nudge
        if acted and reward > -0.2 and reward < 0.2:
            # Seeing plants in best direction is a soft hint; nudge a hair
            reward += 0.05

        # Update learned weights (tiny nudges; bounded)
        lr = self._learn_rate
        self._learned_weights[0] = _clamp(
            self._learned_weights[0] + lr * reward, -5.0, 5.0
        )
        self._learned_weights[1] = _clamp(
            self._learned_weights[1] + lr * reward, -5.0, 5.0
        )
        self._learned_weights[2] = _clamp(
            self._learned_weights[2] - lr * max(0.0, -reward), -5.0, 5.0
        )  # avoid poison more if harmed
        # Energy scaling adapts slower to avoid blowups
        self._learned_weights[3] = _clamp(
            self._learned_weights[3] + 0.25 * lr * reward, -5.0, 5.0
        )

        # Rolling fitness indicators (exp moving averages)
        self.fit_food_gain = 0.9 * self.fit_food_gain + 0.1 * (delta / 50.0)
        if delta > 60.0:
            self.fit_kills = 0.9 * self.fit_kills + 0.1 * 1.0
        elif delta < -60.0:
            self.fit_losses = 0.9 * self.fit_losses + 0.1 * 1.0


# ---------------- DNA mutation with temp & bias ----------------


def mutate_dna(parent_dna: Tuple, temp: float = 1.0, bias_weights=None) -> Tuple:
    """
    Return a mutated copy of parent DNA.
    - temp scales mutation magnitudes (0.7 = gentler, 1.4 = wilder).
    - bias_weights softly pulls genome weights toward a provided vector (learned parent).
    """
    organs, weights, thresholds, flags, mutation = parent_dna

    # Copy to mutate
    o = list(organs)
    w = list(weights)
    t = list(thresholds)
    f = list(flags)
    m = list(mutation)

    weight_sigma, thresh_sigma, flip_p, toggle_p, max_photo, max_spikes, max_cilia = m
    weight_sigma *= temp
    thresh_sigma *= temp

    # Weights mutate with Gaussian noise
    for i in range(len(w)):
        w[i] = _clamp(w[i] + _gauss(0.0, weight_sigma), -5.0, 5.0)

    # Soft bias toward parent's learned weights if provided
    if bias_weights:
        for i in range(len(w)):
            w[i] = 0.8 * w[i] + 0.2 * bias_weights[i]

    # Thresholds: index 0 absolute [0..2.5], others fractional [0.05..0.95]
    for i in range(len(t)):
        newv = t[i] + _gauss(0.0, thresh_sigma)
        if i == 0:
            t[i] = _clamp(newv, 0.0, 2.5)
        else:
            t[i] = _clamp(newv, 0.05, 0.95)

    # Flags: occasional flips
    for i in range(len(f)):
        if _rand() < flip_p:
            f[i] = not f[i]

    # Organs: occasionally toggle (bounded)
    if _rand() < toggle_p:
        choice = _randint(0, 3)
        if choice == 0:  # photo +/- within cap
            o[5] = max(0, min(max_photo, o[5] + _choice((-1, 1))))
        elif choice == 1:  # spikes toggle
            o[7] = max(0, min(max_spikes, o[7] ^ 1))
        elif choice == 2:  # cloak toggle
            o[6] = o[6] ^ 1
        elif choice == 3:  # cilia remains 0/1 bounded
            o[0] = max(0, min(max_cilia, o[0]))

    return (o, w, t, f, m)


# --------------- custom propagator ----------------


class MemoryEvoPropagator(Propagator):
    """Propagator that seeds children with mutated (or cloned) DNA; supports temp & bias control."""

    __slots__ = ("temp", "clone", "bias")

    def __init__(self, host):
        super().__init__(host)
        self.temp = 1.0
        self.clone = False
        self.bias = None  # learned weights from parent, optional

    def set_temp(self, temp: float, clone: bool, learned_weights):
        self.temp = temp
        self.clone = clone
        self.bias = learned_weights

    def make_child(self):
        parent: MemoryEvolver = self.host()  # type: ignore
        dna = (
            parent.dna_organs,
            parent.dna_weights,
            parent.dna_thresholds,
            parent.dna_flags,
            parent.dna_mutation,
        )
        if self.clone:
            # Shallow clone is fine (lists copied, same structure)
            child_dna = (
                list(dna[0]),
                list(dna[1]),
                list(dna[2]),
                list(dna[3]),
                list(dna[4]),
            )
        else:
            child_dna = mutate_dna(dna, temp=self.temp, bias_weights=self.bias)
        return MemoryEvolver(child_dna)
