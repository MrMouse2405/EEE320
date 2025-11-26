"""
Configures and launches the BugBattle application.

Competitors live in the `competitors` module. To add a competitor
to the game, import its class and add it to the  `COMPETITOR_CLASSES`
tuple.

version 1.13
2021-11-23

Python implementation: Greg Phillips
Based on an original design by Scott Knight and a series of
implementations in C++ and Java by Scott Knight and Greg Phillips
"""

import tkinter as tk

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
)
from framework import BugBattle

WORLD_WIDTH = 100
COMPETITOR_CLASSES = (
    # Examples
    AgrarianInstructors.SuperPlant,
    HuntingInstructors.Hunter,
    SyedPabon.GregPhillips,
    Actor2.DNA_CMA_ES_BUG_INFERENCE2,
    Actor3.DNA_CMA_ES_BUG_INFERENCE3,
    Actor4.DNA_CMA_ES_BUG_INFERENCE4,
    Actor5.DNA_CMA_ES_BUG_INFERENCE5,
    Actor6.DNA_CMA_ES_BUG_INFERENCE6,
    TurtleBug.TURTLE,
)


if __name__ == "__main__":
    root = tk.Tk()
    bb = BugBattle(root, WORLD_WIDTH, COMPETITOR_CLASSES)
    bb.master.title("BugBattle Multiprocess")
    bb.master.wm_resizable(False, False)
    bb.mainloop()
