"""
Train Self-Playing CMA-ES Bugs

Improvements:
1. Proper global turn counter tracking
2. Better CMA-ES sigma and bounds
3. Multiple matches per evaluation for stability
4. Separate evolution of early/late game DNA
"""

import cma
import numpy as np

from Competitors.training_actor import DNA_CMA_ES_BUG_RED as RED
from Competitors.training_actor2 import DNA_CMA_ES_BUG_BLUE as BLUE
from evaluate_self_play import run_match

# DNA dimension
DIM = len(RED.DEFAULT_DNA)


# CMA-ES bounds for different parameter types
def get_bounds():
    """Define reasonable bounds for DNA parameters"""
    lower = np.zeros(DIM)
    upper = np.zeros(DIM)

    # For both early (0-31) and late (32-63) game parameters:
    for offset in [0, 32]:
        # Organ thresholds (indices 0-9, 32-41): 100-1200
        # These are "strength remaining after creation" thresholds
        for i in range(10):
            lower[offset + i] = 100
            upper[offset + i] = 1200

        # Organ quantities (indices 10-12, 42-44): 1-6
        for i in range(10, 13):
            lower[offset + i] = 1
            upper[offset + i] = 6

        # Action weights (indices 13-17, 45-49): 0.05-1.0
        for i in range(13, 18):
            lower[offset + i] = 0.05
            upper[offset + i] = 1.0

        # Movement params (indices 18-22, 50-54)
        lower[offset + 18] = 0.5  # Enemy attraction: 0.5-5
        upper[offset + 18] = 5.0
        lower[offset + 19] = 0.5  # Plant attraction: 0.5-6 (important for hunting!)
        upper[offset + 19] = 6.0
        lower[offset + 20] = -5.0  # Poison avoidance: -5 to 0
        upper[offset + 20] = 0.0
        lower[offset + 21] = 0.001  # Energy attraction: 0.001-0.1
        upper[offset + 21] = 0.1
        lower[offset + 22] = 0.3  # Move probability: 0.3-1.0
        upper[offset + 22] = 1.0

        # Combat params (indices 23-26, 55-58)
        lower[offset + 23] = 0.4  # Min strength ratio: 0.4-2.0
        upper[offset + 23] = 2.0
        lower[offset + 24] = 300  # Min absolute strength: 300-1000
        upper[offset + 24] = 1000
        lower[offset + 25] = 0.1  # Cloak threshold: 0.1-0.5
        upper[offset + 25] = 0.5
        lower[offset + 26] = 0.8  # Pursuit ratio: 0.8-2.5
        upper[offset + 26] = 2.5

        # Reproduction params (indices 27-31, 59-63)
        lower[offset + 27] = 600  # Min strength: 600-1400
        upper[offset + 27] = 1400
        lower[offset + 28] = 0.15  # Energy fraction: 0.15-0.45
        upper[offset + 28] = 0.45
        lower[offset + 29] = 2  # Max offspring: 2-8
        upper[offset + 29] = 8
        lower[offset + 30] = 0.1  # Pop scaling: 0.1-0.8
        upper[offset + 30] = 0.8
        lower[offset + 31] = 0.2  # Repro probability: 0.2-0.7
        upper[offset + 31] = 0.7

    return lower, upper


def clip_to_bounds(dna, lower, upper):
    """Clip DNA to valid bounds"""
    return np.clip(dna, lower, upper)


def evaluate_with_multiple_matches(dnaA, dnaB, num_matches=3):
    """
    Run multiple matches and average rewards for more stable evaluation.
    Also run reverse matchup for symmetry.
    """
    rewards_A = []
    rewards_B = []

    for _ in range(num_matches):
        # Reset turn counters
        RED.global_turn = 0
        BLUE.global_turn = 0

        # Run match A vs B
        rA, rB = run_match(
            dnaA, dnaB, world_size=35, stagnation_limit=600, hard_turn_cap=2500
        )
        rewards_A.append(rA)
        rewards_B.append(rB)

    # Return average rewards
    return np.mean(rewards_A), np.mean(rewards_B)


def train_selfplay():
    """Main training loop with improved CMA-ES configuration"""

    # Load existing top performers
    RED.load_top_list()
    BLUE.load_top_list()

    # Get initial DNA
    x0_A = RED.choose_initial_dna()
    x0_B = BLUE.choose_initial_dna()

    # Get bounds
    lower, upper = get_bounds()

    # Clip initial DNA to bounds
    x0_A = clip_to_bounds(x0_A, lower, upper)
    x0_B = clip_to_bounds(x0_B, lower, upper)

    # CMA-ES options
    sigma0 = 0.3  # Initial step size (relative to bounds)

    opts_A = {
        "bounds": [lower.tolist(), upper.tolist()],
        "popsize": 12,  # Population size
        "maxiter": 1000,
        "verb_disp": 1,
        "verb_log": 0,
        "CMA_diagonal": True,  # Use diagonal covariance for efficiency
    }

    opts_B = {
        "bounds": [lower.tolist(), upper.tolist()],
        "popsize": 12,
        "maxiter": 1000,
        "verb_disp": 1,
        "verb_log": 0,
        "CMA_diagonal": True,
    }

    # Create CMA-ES optimizers
    es_A = cma.CMAEvolutionStrategy(x0_A, sigma0, opts_A)
    es_B = cma.CMAEvolutionStrategy(x0_B, sigma0, opts_B)

    generation = 0
    best_reward_A = float("-inf")
    best_reward_B = float("-inf")

    print("=" * 60)
    print("Starting Self-Play CMA-ES Training")
    print(f"DNA Dimension: {DIM}")
    print(f"Population Size: {opts_A['popsize']}")
    print("=" * 60)

    while not es_A.stop() and not es_B.stop():
        generation += 1

        # Sample populations
        pop_A = es_A.ask()
        pop_B = es_B.ask()

        # Clip to bounds (CMA-ES should respect bounds but double-check)
        pop_A = [clip_to_bounds(dna, lower, upper) for dna in pop_A]
        pop_B = [clip_to_bounds(dna, lower, upper) for dna in pop_B]

        fitness_A = []
        fitness_B = []

        print(f"\n--- Generation {generation} ---")

        # Evaluate each pair
        for i, (dnaA, dnaB) in enumerate(zip(pop_A, pop_B)):
            print(f"  Match {i + 1}/{len(pop_A)}...", end=" ", flush=True)

            rA, rB = evaluate_with_multiple_matches(dnaA, dnaB, num_matches=2)

            # CMA-ES minimizes, so negate rewards
            fitness_A.append(-rA)
            fitness_B.append(-rB)

            print(f"RED: {rA:,.0f}, BLUE: {rB:,.0f}")

        # Tell CMA-ES the results
        es_A.tell(pop_A, fitness_A)
        es_B.tell(pop_B, fitness_B)

        # Track best rewards (remember: we negated for minimization)
        current_best_A = -es_A.result.fbest
        current_best_B = -es_B.result.fbest

        if current_best_A > best_reward_A:
            best_reward_A = current_best_A
            print(f"  *** NEW BEST RED: {best_reward_A:,.0f} ***")

        if current_best_B > best_reward_B:
            best_reward_B = current_best_B
            print(f"  *** NEW BEST BLUE: {best_reward_B:,.0f} ***")

        # Summary
        print(f"\n  Generation {generation} Summary:")
        print(f"    RED  - Best: {current_best_A:,.0f}, Sigma: {es_A.sigma:.4f}")
        print(f"    BLUE - Best: {current_best_B:,.0f}, Sigma: {es_B.sigma:.4f}")

        # Save top performers
        RED.top_dna.append((current_best_A, es_A.result.xbest.copy()))
        RED.top_dna = sorted(RED.top_dna, key=lambda x: x[0], reverse=True)[: RED.TOP_K]
        np.save(RED.TOP_FILE, np.array(RED.top_dna, dtype=object))

        BLUE.top_dna.append((current_best_B, es_B.result.xbest.copy()))
        BLUE.top_dna = sorted(BLUE.top_dna, key=lambda x: x[0], reverse=True)[
            : BLUE.TOP_K
        ]
        np.save(BLUE.TOP_FILE, np.array(BLUE.top_dna, dtype=object))

        # Every 10 generations, print best DNA summary
        if generation % 10 == 0:
            print("\n" + "=" * 60)
            print(f"Generation {generation} - DNA Summary")
            print("=" * 60)
            print_dna_summary(es_A.result.xbest, "RED")
            print_dna_summary(es_B.result.xbest, "BLUE")

    print("\n" + "=" * 60)
    print("Training Complete!")
    print(f"Best RED Reward: {best_reward_A:,.0f}")
    print(f"Best BLUE Reward: {best_reward_B:,.0f}")
    print("=" * 60)


def print_dna_summary(dna, name):
    """Print human-readable summary of key DNA parameters"""
    print(f"\n{name} Key Parameters:")
    print(f"  Early Game:")
    print(f"    Cilia target: {dna[10]:.1f}, PhotoGlands: {dna[11]:.1f}")
    print(f"    Combat weight: {dna[13]:.2f}, Repro weight: {dna[14]:.2f}")
    print(f"    Enemy attract: {dna[18]:.2f}, Plant attract: {dna[19]:.2f}")
    print(f"    Min attack ratio: {dna[23]:.2f}, Min strength: {dna[24]:.0f}")
    print(f"  Late Game:")
    print(f"    Cilia target: {dna[42]:.1f}, PhotoGlands: {dna[43]:.1f}")
    print(f"    Combat weight: {dna[45]:.2f}, Repro weight: {dna[46]:.2f}")
    print(f"    Enemy attract: {dna[50]:.2f}, Plant attract: {dna[51]:.2f}")
    print(f"    Min attack ratio: {dna[55]:.2f}, Min strength: {dna[56]:.0f}")


if __name__ == "__main__":
    train_selfplay()
