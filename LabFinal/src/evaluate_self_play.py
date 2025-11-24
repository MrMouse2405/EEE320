import sys
import time
from multiprocessing import Pipe

import numpy as np
from AgrarianInstructors import SuperPlant
from framework import Simulation
from GregPhillips import GregPhillips
from HuntingInstructors import Hunter
from training_actor import DNA_CMA_ES_BUG_RED
from training_actor2 import DNA_CMA_ES_BUG_BLUE

# RL agents only
RL_CLASSES = (DNA_CMA_ES_BUG_RED, DNA_CMA_ES_BUG_BLUE)

# All competitors placed in world
COMPETITORS = (
    DNA_CMA_ES_BUG_RED,
    DNA_CMA_ES_BUG_BLUE,
    Hunter,
    SuperPlant,
)

########################################################
#                 MAIN MATCH FUNCTION
########################################################


def run_match(
    dnaA,
    dnaB,
    world_size=50,
    stagnation_limit=800,
    tolerance=1,
    hard_turn_cap=3000,  # <--- NEW HARD STOP
):
    """
    Run one self-play match between RED and BLUE.

    - Ends early if stagnation detected
    - Ends early if hard_turn_cap exceeded
    - Punishes loser using reward_timeout()
    """

    # Assign initial DNA
    DNA_CMA_ES_BUG_RED.DEFAULT_DNA = np.copy(dnaA)
    DNA_CMA_ES_BUG_BLUE.DEFAULT_DNA = np.copy(dnaB)

    # Reset reward
    DNA_CMA_ES_BUG_RED.reward_score = 0
    DNA_CMA_ES_BUG_BLUE.reward_score = 0

    # Fake pipe (no GUI)
    sim_end, gui_end = Pipe()
    sim = Simulation(sim_end, world_size)
    sim.reset(COMPETITORS, interval=0.0)
    sim.running = True

    ########################################################
    #   Stagnation tracking — RL species only
    ########################################################
    last_rl_counts = [cls.instance_count() for cls in RL_CLASSES]
    stagnant_turns = 0

    ########################################################
    # MAIN LOOP
    ########################################################
    while True:
        sim.world.do_turn()
        sim.turn_count += 1
        winner = sim.check_win()

        if winner:
            print(f"\n {winner.__name__}: WON!")
            sys.stdout.flush()
            break

        # HARD TURN LIMIT --------------------------
        if sim.turn_count >= hard_turn_cap:
            print(f"\n[Hard Stop] Turn {sim.turn_count}: TIME LIMIT EXCEEDED")

            red_pop = DNA_CMA_ES_BUG_RED.instance_count()
            blue_pop = DNA_CMA_ES_BUG_BLUE.instance_count()

            # Apply timeout reward (punishes loser)
            DNA_CMA_ES_BUG_RED.reward_timeout(red_pop, blue_pop)
            DNA_CMA_ES_BUG_BLUE.reward_timeout(blue_pop, red_pop)

            sim.game_over = True
            break
        # -------------------------------------------

        # RL population only
        current_rl_counts = [cls.instance_count() for cls in RL_CLASSES]

        # Stagnation detection
        stagnant = True
        for cc, lc in zip(current_rl_counts, last_rl_counts):
            if cc == 0:  # dead species shouldn't affect stagnation
                continue
            if abs(cc - lc) > tolerance:
                stagnant = False
                break

        stagnant_turns = stagnant_turns + 1 if stagnant else 0

        if stagnant_turns >= stagnation_limit:
            print(f"\nStagnation detected at turn {sim.turn_count}", end="\r")

            red_pop = DNA_CMA_ES_BUG_RED.instance_count()
            blue_pop = DNA_CMA_ES_BUG_BLUE.instance_count()

            DNA_CMA_ES_BUG_RED.reward_timeout(red_pop, blue_pop)
            DNA_CMA_ES_BUG_BLUE.reward_timeout(blue_pop, red_pop)

            sim.game_over = True
            break

        # Both dead → no reward change
        if (
            DNA_CMA_ES_BUG_RED.instance_count() == 0
            and DNA_CMA_ES_BUG_BLUE.instance_count() == 0
        ):
            print(f"\nTurn {sim.turn_count}: Both RL agents dead")
            sim.game_over = True
            break

        ########################################################
        # Console Output
        ########################################################
        status = f"Turn {sim.turn_count:4d} |"
        for c in COMPETITORS:
            status += f" {c.__name__}: {c.instance_count():4d} |"
        print(status, end="\r")
        sys.stdout.flush()

        last_rl_counts = current_rl_counts

    ########################################################
    # DONE — Return final reward scores for CMA-ES
    ########################################################
    return DNA_CMA_ES_BUG_RED.reward_score, DNA_CMA_ES_BUG_BLUE.reward_score
