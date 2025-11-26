"""
Headless Self-Play Match Evaluation
Supports unlimited competitors, including newly added bugs.
"""

import random
import sys

import numpy as np

# ---------------------------------------------------------
# IMPORT ALL COMPETITORS
# ---------------------------------------------------------
from Competitors import (
    Actor2,
    Actor3,
    Actor4,
    Actor5,
    Actor6,
    AgrarianInstructors,
    HuntingInstructors,
    SyedPabon,
    TurtleBug,
    training_actor,
    training_actor2,
)
from shared import Soil, World

# =========================================================
# RL AGENTS (THE ONES WE ARE TRAINING)
# =========================================================
RL_CLASSES = (
    training_actor.DNA_CMA_ES_BUG_RED,
    training_actor2.DNA_CMA_ES_BUG_BLUE,
)

# =========================================================
# AUTO-DISCOVER EXTRA COMPETITORS
# =========================================================
NON_RL_CLASSES = tuple(
    cls
    for cls in [
        SyedPabon.GregPhillips,
        HuntingInstructors.Hunter,
        AgrarianInstructors.SuperPlant,
        Actor2.DNA_CMA_ES_BUG_INFERENCE2,
        Actor3.DNA_CMA_ES_BUG_INFERENCE3,
        Actor4.DNA_CMA_ES_BUG_INFERENCE4,
        Actor5.DNA_CMA_ES_BUG_INFERENCE5,
        Actor6.DNA_CMA_ES_BUG_INFERENCE6,
        TurtleBug.TURTLE,
    ]
    if cls not in RL_CLASSES
)

# Final competitor list
COMPETITORS = RL_CLASSES + NON_RL_CLASSES

# =========================================================
# SIMULATION CONSTANTS
# =========================================================
INITIAL_PLANT_PROBABILITY = 0.12
START_STRENGTH = 1500
N_CREATURES = 3  # can be made per-competitor


# =========================================================
# UNIVERSAL INSTANCE COUNT RESET
# =========================================================
def reset_instance_counts():
    for cls in COMPETITORS:
        # Every competitor class has a private __instance_count
        # but with different mangled names.
        for attr in dir(cls):
            if attr.endswith("__instance_count"):
                setattr(cls, attr, 0)


# =========================================================
# RUN ONE MATCH
# =========================================================
def run_match(
    dnaA,
    dnaB,
    world_size=100,
    stagnation_limit=800,
    tolerance=1,
    hard_turn_cap=3000,
):
    """
    Run one headless match between RL agents against all competitors.
    RL agents are always RED and BLUE (dnaA, dnaB).
    """

    RED = RL_CLASSES[0]
    BLUE = RL_CLASSES[1]

    # Set starting DNA
    RED.DEFAULT_DNA = np.copy(dnaA)
    BLUE.DEFAULT_DNA = np.copy(dnaB)

    # Reset rewards
    RED.reward_score = 0
    BLUE.reward_score = 0

    # Reset global turn counters
    RED.global_turn = 0
    BLUE.global_turn = 0

    reset_instance_counts()

    # Create world
    world = World(world_size)

    # Grow early plants
    for i in range(world_size * world_size):
        c = world.creature_at(i)
        if isinstance(c, Soil) and random.random() < INITIAL_PLANT_PROBABILITY:
            c.become_plant()

    # Spawn all competitors
    for competitor in COMPETITORS:
        for _ in range(N_CREATURES):
            instance = competitor()
            instance.f_feed(START_STRENGTH)
            world.place(instance, random.randrange(world_size * world_size))

    last_rl_counts = [cls.instance_count() for cls in RL_CLASSES]
    stagnant_turns = 0
    turn_count = 0

    # =====================================================
    # MAIN LOOP
    # =====================================================
    while True:
        RED.global_turn = turn_count
        BLUE.global_turn = turn_count

        world.do_turn()
        turn_count += 1

        # Winner check
        alive = [cls for cls in COMPETITORS if cls.instance_count() > 0]

        if len(alive) == 1:
            winner = alive[0]
            print(f"\n>>> {winner.__name__} WINS! (Turn {turn_count})")

            if winner is RED:
                RED.reward_win()
                BLUE.reward_loss()
            elif winner is BLUE:
                BLUE.reward_win()
                RED.reward_loss()
            break

        # Hard limit
        if turn_count >= hard_turn_cap:
            print(f"\n>>> TIME LIMIT (Turn {turn_count})")
            r = RED.instance_count()
            b = BLUE.instance_count()
            RED.reward_timeout(r, b)
            BLUE.reward_timeout(b, r)
            break

        # RL pop stagnation
        rl_counts = [cls.instance_count() for cls in RL_CLASSES]
        stagnant = True
        for new, old in zip(rl_counts, last_rl_counts):
            if new == 0:
                continue
            if abs(new - old) > tolerance:
                stagnant = False
                break

        stagnant_turns = stagnant_turns + 1 if stagnant else 0

        if stagnant_turns >= stagnation_limit:
            print(f"\n>>> STAGNATION (Turn {turn_count})")
            r = RED.instance_count()
            b = BLUE.instance_count()
            RED.reward_timeout(r, b)
            BLUE.reward_timeout(b, r)
            break

        # RL extinction
        if RL_CLASSES[0].instance_count() == 0 and RL_CLASSES[1].instance_count() == 0:
            print(f"\n>>> MUTUAL EXTINCTION (Turn {turn_count})")
            break

        # Status output
        if turn_count % 50 == 0:
            msg = f"Turn {turn_count:4d} |"
            for cls in COMPETITORS:
                msg += f" {cls.__name__[:10]:10s}: {cls.instance_count():3d} |"
            print(msg, end="\r")
            sys.stdout.flush()

        last_rl_counts = rl_counts

    return RED.reward_score, BLUE.reward_score


# =========================================================
# TEST MATCH
# =========================================================
if __name__ == "__main__":
    RED = RL_CLASSES[0]
    BLUE = RL_CLASSES[1]

    dnaA = np.copy(RED.DEFAULT_DNA)
    dnaB = np.copy(BLUE.DEFAULT_DNA)

    print("Running match with many competitors...")
    print("=" * 60)

    rA, rB = run_match(
        dnaA,
        dnaB,
        world_size=30,
        stagnation_limit=400,
        hard_turn_cap=1500,
    )

    print("\n" + "=" * 60)
    print(f"Final Rewards:")
    print(f"  RED:  {rA:,.0f}")
    print(f"  BLUE: {rB:,.0f}")
    print("=" * 60)
