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

from competitors.dna import Evolver, MemoryEvolver, SyedMalware, SyedPabon
from competitors.examples import AgrarianInstructors, HuntingInstructors
from competitors.vanilla import (
    AggressorBug,
    AmbusherBug,
    CloakHunterBug,
    DefenderBug,
    EvaderBug,
    # FarmerBug,
    HiveBug,
    HybridPlantBug,
    MinerBug,
    MirrorBug,
    NomadBug,
    PacifistBug,
    PoisonDropperBug,
    PredatorBug,
    ScoutBug,
    SelfDestructBug,
    SniperBug,
    SwarmBug,
    TankBug,
    VampireBug,
)
from framework import BugBattle

WORLD_WIDTH = 100
COMPETITOR_CLASSES = (
    # Examples
    HuntingInstructors.Hunter,
    AgrarianInstructors.SuperPlant,
    # Genetic Algorithm Bugs
    Evolver.Evolver,
    MemoryEvolver.MemoryEvolver,
    # Normal Strategy Bugs
    AggressorBug.AggressorBug,
    AmbusherBug.AmbusherBug,
    CloakHunterBug.CloakHunterBug,
    DefenderBug.DefenderBug,
    EvaderBug.EvaderBug,
    # FarmerBug.FarmerBug,
    # HiveBug.HiveBug,
    # HybridPlantBug.HybridPlantBug,
    # MinerBug.MinerBug,
    # MirrorBug.MirrorBug,
    # NomadBug.NomadBug,
    # PacifistBug.PacifistBug,
    # PoisonDropperBug.PoisonDropperBug,
    # PredatorBug.PredatorBug,
    # ScoutBug.ScoutBug,
    # SelfDestructBug.SelfDestructBug,
    # SniperBug.SniperBug,
    # SwarmBug.SwarmBug,
    # TankBug.TankBug,
    # VampireBug.VampireBug,
    SyedPabon.GregPhillips,
    SyedMalware.MalwareBug,
)


if __name__ == "__main__":
    root = tk.Tk()
    bb = BugBattle(root, WORLD_WIDTH, COMPETITOR_CLASSES)
    bb.master.title("BugBattle Multiprocess")
    bb.master.wm_resizable(False, False)
    bb.mainloop()
