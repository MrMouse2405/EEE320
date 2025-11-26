import tkinter as tk
from turtle import Turtle

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
from framework import BugBattle

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
    TurtleBug.TURTLE,
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
