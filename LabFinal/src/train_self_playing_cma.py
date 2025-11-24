import cma
import numpy as np
from evaluate_self_play import run_match
from training_actor import DNA_CMA_ES_BUG_RED as SRLV
from training_actor2 import DNA_CMA_ES_BUG_BLUE as SRLV2

DIM = len(SRLV.DEFAULT_DNA)


def train_selfplay():
    SRLV.load_top_list()
    SRLV2.load_top_list()

    x0_A = SRLV.choose_initial_dna()
    x0_B = SRLV2.choose_initial_dna()

    sigma0 = 0.5

    es_A = cma.CMAEvolutionStrategy(x0_A, sigma0)
    es_B = cma.CMAEvolutionStrategy(x0_B, sigma0)

    while True:
        pop_A = es_A.ask()
        pop_B = es_B.ask()

        fitness_A = []
        fitness_B = []

        for dnaA, dnaB in zip(pop_A, pop_B):
            rA, rB = run_match(dnaA, dnaB, 25)
            fitness_A.append(-rA)  # CMA minimizes
            fitness_B.append(-rB)

        es_A.tell(pop_A, fitness_A)
        es_B.tell(pop_B, fitness_B)

        print("Best A Reward:", -es_A.result.fbest)
        print("Best B Reward:", -es_B.result.fbest)

        # Save top performers
        SRLV.top_dna.append((-es_A.result.fbest, es_A.result.xbest))
        SRLV.export_top_list()

        SRLV2.top_dna.append((-es_B.result.fbest, es_B.result.xbest))
        SRLV2.export_top_list()


if __name__ == "__main__":
    train_selfplay()
