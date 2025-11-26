"""
Convert trained DNA weights from numpy format to plain Python.

Usage:
    python convert_weights.py [input_file] [output_file]

    Default: dna_top10.npy -> dna_weights.py

This creates a Python file containing the DNA as a plain list that can be
imported without numpy.
"""

import sys

import numpy as np


def convert_weights(input_file="dna_top10.npy", output_file="dna_weights.py"):
    """Convert numpy weights file to plain Python list."""

    try:
        # Load the numpy file
        top_dna_list = list(np.load(input_file, allow_pickle=True))

        if len(top_dna_list) == 0:
            print(f"Error: No DNA entries found in {input_file}")
            return False

        # Get the best DNA (highest reward)
        best_entry = top_dna_list[0]
        best_reward = best_entry[0]
        best_dna = best_entry[1]

        # Convert to plain Python list
        dna_list = [float(x) for x in best_dna]

        # Generate Python file content
        content = f'''"""
Auto-generated DNA weights from training.
Best reward: {best_reward:,.0f}
DNA length: {len(dna_list)}
"""

# Best trained DNA as plain Python list
TRAINED_DNA = {dna_list}
'''

        # Write to file
        with open(output_file, "w") as f:
            f.write(content)

        print(f"Successfully converted {input_file} -> {output_file}")
        print(f"  Best reward: {best_reward:,.0f}")
        print(f"  DNA length: {len(dna_list)}")

        # Also print the DNA for easy copy-paste
        print(f"\nDNA values:")
        print(f"TRAINED_DNA = {dna_list}")

        return True

    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return False
    except Exception as e:
        print(f"Error converting weights: {e}")
        return False


def print_default_dna():
    """Print the default DNA for copy-paste if no trained weights exist."""

    default_dna = [
        # EARLY GAME (0-31)
        200.0,
        100.0,
        300.0,
        800.0,
        600.0,
        350.0,
        250.0,
        1200.0,
        300.0,
        1000.0,
        4.0,
        2.0,
        0.0,
        0.85,
        0.5,
        0.05,
        0.05,
        0.2,
        3.0,
        2.5,
        -2.0,
        0.02,
        0.9,
        0.7,
        500.0,
        0.2,
        1.4,
        800.0,
        0.35,
        5.0,
        0.35,
        0.5,
        # LATE GAME (32-63)
        150.0,
        50.0,
        200.0,
        500.0,
        400.0,
        300.0,
        200.0,
        500.0,
        250.0,
        600.0,
        6.0,
        2.0,
        0.0,
        0.95,
        0.2,
        0.15,
        0.1,
        0.1,
        4.0,
        1.0,
        -1.5,
        0.01,
        0.95,
        0.5,
        350.0,
        0.15,
        1.2,
        1000.0,
        0.3,
        3.0,
        0.5,
        0.25,
    ]

    print("\nDefault DNA (no training file found):")
    print(f"DEFAULT_DNA = {default_dna}")


if __name__ == "__main__":
    # Parse command line arguments
    input_file = sys.argv[1] if len(sys.argv) > 1 else "dna_top10.npy"
    output_file = sys.argv[2] if len(sys.argv) > 2 else "dna_weights.py"

    success = convert_weights(input_file, output_file)

    if not success:
        print_default_dna()
