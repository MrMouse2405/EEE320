import tkinter as tk

from framework import BugBattle
from shared import World
from training_actor import SimpleRLV3 as SRLV
from training_actor2 import SimpleRLV3 as SRLV2

COMPETITOR_CLASSES = (SRLV2, SRLV)

WORLD_SIZE = 100


def main():
    root = tk.Tk()
    bb = BugBattle(root, WORLD_SIZE, COMPETITOR_CLASSES)
    bb.master.title("BugBattle Multiprocess")  # type: ignore
    bb.master.wm_resizable(False, False)  # type: ignore
    bb.mainloop()


if __name__ == "__main__":
    main()
