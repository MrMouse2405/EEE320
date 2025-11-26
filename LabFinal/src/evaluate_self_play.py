"""
Headless Self-Play Match Evaluation

This version doesn't require tkinter/GUI - runs simulation directly.
"""

import random
import sys

import numpy as np

from Competitors import (
    Actor2,
    Actor3,
    Actor4,
    Actor5,
    AgrarianInstructors,
    HuntingInstructors,
    SyedPabon,
    TurtleBug,
    training_actor,
    training_actor2,
)
from shared import (
    Soil,
    World,
)

# RL agents only
RL_CLASSES = (training_actor.DNA_CMA_ES_BUG_RED, training_actor2.DNA_CMA_ES_BUG_BLUE)

# All competitors
COMPETITORS = (
    training_actor.DNA_CMA_ES_BUG_RED,
    training_actor2.DNA_CMA_ES_BUG_BLUE,
    SyedPabon.GregPhillips,
    HuntingInstructors.Hunter,
    AgrarianInstructors.SuperPlant,
    Actor2.DNA_CMA_ES_BUG_INFERENCE2,
    Actor3.DNA_CMA_ES_BUG_INFERENCE3,
    Actor4.DNA_CMA_ES_BUG_INFERENCE4,
    Actor5.DNA_CMA_ES_BUG_INFERENCE5,
)

# Simulation constants
INITIAL_PLANT_PROBABILITY = 0.12
START_STRENGTH = 1500
N_CREATURES = 3


def reset_instance_counts():
    """Reset all instance counts"""
    DNA_CMA_ES_BUG_RED._DNA_CMA_ES_BUG_RED__instance_count = 0
    DNA_CMA_ES_BUG_BLUE._DNA_CMA_ES_BUG_BLUE__instance_count = 0
    Hunter._Hunter__instance_count = 0
    SuperPlant._SuperPlant__instance_count = 0


def run_match(
    dnaA,
    dnaB,
    world_size=100,
    stagnation_limit=800,
    tolerance=1,
    hard_turn_cap=3000,
):
    """
    Run one self-play match between RED and BLUE.

    Returns: (reward_red, reward_blue)
    """

    # Assign DNA
    DNA_CMA_ES_BUG_RED.DEFAULT_DNA = np.copy(dnaA)
    DNA_CMA_ES_BUG_BLUE.DEFAULT_DNA = np.copy(dnaB)

    # Reset rewards
    DNA_CMA_ES_BUG_RED.reward_score = 0
    DNA_CMA_ES_BUG_BLUE.reward_score = 0

    # Reset global turn counters
    DNA_CMA_ES_BUG_RED.global_turn = 0
    DNA_CMA_ES_BUG_BLUE.global_turn = 0

    # Reset instance counts
    reset_instance_counts()

    # Create world
    world = World(world_size)

    # Grow initial plants
    for i in range(world_size * world_size):
        creature = world.creature_at(i)
        if isinstance(creature, Soil) and random.random() < INITIAL_PLANT_PROBABILITY:
            creature.become_plant()

    # Populate with competitors
    for competitor in COMPETITORS:
        for _ in range(N_CREATURES):
            c = competitor()
            c.f_feed(START_STRENGTH)
            world.place(c, random.randrange(world_size * world_size))

    # Stagnation tracking
    last_rl_counts = [cls.instance_count() for cls in RL_CLASSES]
    stagnant_turns = 0
    turn_count = 0

    # Main simulation loop
    while True:
        # Update global turn counters BEFORE do_turn
        DNA_CMA_ES_BUG_RED.global_turn = turn_count
        DNA_CMA_ES_BUG_BLUE.global_turn = turn_count

        world.do_turn()
        turn_count += 1

        # Check for winner
        live_competitors = []
        for competitor in COMPETITORS:
            if competitor.instance_count() > 0:
                live_competitors.append(competitor)

        if len(live_competitors) == 1:
            winner = live_competitors[0]
            print(f"\n>>> {winner.__name__} WINS! (Turn {turn_count})")

            # Assign win/loss rewards
            if winner is DNA_CMA_ES_BUG_RED:
                DNA_CMA_ES_BUG_RED.reward_win()
                DNA_CMA_ES_BUG_BLUE.reward_loss()
            elif winner is DNA_CMA_ES_BUG_BLUE:
                DNA_CMA_ES_BUG_BLUE.reward_win()
                DNA_CMA_ES_BUG_RED.reward_loss()
            break

        # Hard turn limit
        if turn_count >= hard_turn_cap:
            print(f"\n>>> TIME LIMIT (Turn {turn_count})")

            red_pop = DNA_CMA_ES_BUG_RED.instance_count()
            blue_pop = DNA_CMA_ES_BUG_BLUE.instance_count()

            DNA_CMA_ES_BUG_RED.reward_timeout(red_pop, blue_pop)
            DNA_CMA_ES_BUG_BLUE.reward_timeout(blue_pop, red_pop)
            break

        # Current RL populations
        current_rl_counts = [cls.instance_count() for cls in RL_CLASSES]

        # Stagnation detection
        stagnant = True
        for cc, lc in zip(current_rl_counts, last_rl_counts):
            if cc == 0:
                continue
            if abs(cc - lc) > tolerance:
                stagnant = False
                break

        stagnant_turns = stagnant_turns + 1 if stagnant else 0

        if stagnant_turns >= stagnation_limit:
            print(f"\n>>> STAGNATION (Turn {turn_count})")

            red_pop = DNA_CMA_ES_BUG_RED.instance_count()
            blue_pop = DNA_CMA_ES_BUG_BLUE.instance_count()

            DNA_CMA_ES_BUG_RED.reward_timeout(red_pop, blue_pop)
            DNA_CMA_ES_BUG_BLUE.reward_timeout(blue_pop, red_pop)
            break

        # Both RL agents dead
        if (
            DNA_CMA_ES_BUG_RED.instance_count() == 0
            and DNA_CMA_ES_BUG_BLUE.instance_count() == 0
        ):
            print(f"\n>>> MUTUAL EXTINCTION (Turn {turn_count})")
            break

        # Progress output
        if turn_count % 50 == 0:
            status = f"Turn {turn_count:4d} |"
            for c in COMPETITORS:
                status += f" {c.__name__[:8]:8s}: {c.instance_count():3d} |"
            print(status, end="\r")
            sys.stdout.flush()

        last_rl_counts = current_rl_counts

    return DNA_CMA_ES_BUG_RED.reward_score, DNA_CMA_ES_BUG_BLUE.reward_score


if __name__ == "__main__":
    print("Running test match with default DNA...")
    print("=" * 60)

    dnaA = np.copy(DNA_CMA_ES_BUG_RED.DEFAULT_DNA)
    dnaB = np.copy(DNA_CMA_ES_BUG_BLUE.DEFAULT_DNA)

    rA, rB = run_match(
        dnaA, dnaB, world_size=30, stagnation_limit=400, hard_turn_cap=1500
    )

    print()
    print("=" * 60)
    print(f"Final Rewards:")
    print(f"  RED:  {rA:,.0f}")
    print(f"  BLUE: {rB:,.0f}")
    print("=" * 60)
