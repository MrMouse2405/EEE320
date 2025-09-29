import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import skfuzzy as fuzz
from skfuzzy import control as ctrl

"""
  Inputs
"""
# Rationale: Very high / very low flying aircrafts maybe present threat. In feet.
Altitude = ctrl.Antecedent(np.arange(0, 60_000, 1), "Altitude")
Altitude["low"] = fuzz.trimf(Altitude.universe, [0, 0, 10_000])
Altitude["medium"] = fuzz.trimf(Altitude.universe, [8_000, 25_000, 40_000])
Altitude["high"] = fuzz.trimf(Altitude.universe, [35_000, 60_000, 60_000])

# Rationale: high speed may indiciate military or fast inbound contact. In knots.
Speed = ctrl.Antecedent(np.arange(0, 1000, 1), "Speed")
Speed["slow"] = fuzz.trimf(Speed.universe, [0, 0, 250])
Speed["medium"] = fuzz.trimf(Speed.universe, [200, 500, 800])
Speed["fast"] = fuzz.trimf(Speed.universe, [600, 1000, 1000])

# Rationale: Closest Point of Approach, small CAP -> high threat. In nautical miles.
CAP = ctrl.Antecedent(np.arange(0, 50, 1), "CAP")
CAP["close"] = fuzz.trimf(CAP.universe, [0, 0, 5])
CAP["medium"] = fuzz.trimf(CAP.universe, [3, 12, 25])
CAP["far"] = fuzz.trimf(CAP.universe, [20, 50, 50])


# Rationale: shorter range → greater immediate threat. In nautical miles.
# range as in distance to task group
Range = ctrl.Antecedent(np.arange(0, 300, 1), label="Range")
Range["close"] = fuzz.trimf(Range.universe, [0, 0, 30])
Range["low"] = fuzz.trimf(Range.universe, [20, 80, 160])
Range["far"] = fuzz.trimf(Range.universe, [140, 300, 300])

"""
    Outputs
"""
# Outputs
ThreatRating = ctrl.Consequent(np.arange(0, 1, 0.05), label="ThreatRating")
ThreatRating["low"] = fuzz.trimf(ThreatRating.universe, [0, 0, 0.35])
ThreatRating["medium"] = fuzz.trimf(ThreatRating.universe, [0.3, 0.5, 0.7])
ThreatRating["high"] = fuzz.trimf(ThreatRating.universe, [0.65, 1, 1])

"""
    Inference Rules
"""

rule1 = ctrl.Rule(
    # if
    Altitude["low"] & Speed["fast"] & Range["close"] & CAP["close"],
    # then
    ThreatRating["high"],
)

rule2 = ctrl.Rule(
    # if
    Altitude["high"] & Speed["slow"] & Range["far"] & CAP["far"],
    # then
    ThreatRating["low"],
)

rule3 = ctrl.Rule(
    # if
    Altitude["medium"] & Speed["medium"] & Range["medium"] & CAP["medium"],
    # then
    ThreatRating["medium"],
)

rule4 = ctrl.Rule(
    # if
    Altitude["low"] & Speed["fast"] & Range["far"] & CAP["close"],
    # then
    ThreatRating["medium"],
)

rule5 = ctrl.Rule(
    # if
    Range["close"],
    # then
    ThreatRating["medium"],
)

rule6 = ctrl.Rule(
    # if
    Range["far"],
    # then
    ThreatRating["low"],
)

rule7 = ctrl.Rule(
    # if
    Range["medium"],
    # then
    ThreatRating["low"],
)


def main():
    [x.view() for x in [Altitude, Speed, Range, CAP, ThreatRating]]
    plt.show()


if __name__ == "__main__":
    main()
