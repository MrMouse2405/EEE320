import tkinter as tk
from turtle import Turtle

from Competitors import (
    AgrarianInstructors,
    HuntingInstructors,
    training_actor,
    training_actor2,
)
from framework import BugBattle

# RL agents only
RL_CLASSES = (training_actor.DNA_CMA_ES_BUG_RED, training_actor2.DNA_CMA_ES_BUG_BLUE)

# All competitors
COMPETITORS = (
    training_actor.DNA_CMA_ES_BUG_RED,
    training_actor2.DNA_CMA_ES_BUG_BLUE,
    HuntingInstructors.Hunter,
    AgrarianInstructors.SuperPlant,
)
WORLD_SIZE = 100


def main():
    root = tk.Tk()
    bb = BugBattle(root, WORLD_SIZE, COMPETITORS)
    bb.master.title("BugBattle Multiprocess")  # type: ignore
    bb.master.wm_resizable(False, False)  # type: ignore
    bb.mainloop()


if __name__ == "__main__":
    main()
