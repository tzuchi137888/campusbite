"""Rebuild the clearly labelled synthetic demo dataset; never real-world evidence."""
import csv
import random
from pathlib import Path


def generate():
    rng = random.Random(20261005)
    path = Path(__file__).parent / "data" / "synthetic_meals.csv"
    path.parent.mkdir(exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["source", "meal", "party", "duration_min"])
        for meal, base in [("rice", 21), ("noodles", 25), ("cafe", 36)]:
            for party in range(1, 7):
                for _ in range(100):
                    duration = max(8, rng.gauss(base + 1.5 * (party - 1), 5))
                    writer.writerow(["synthetic", meal, party, round(duration, 2)])
    print(f"Generated 1800 synthetic sessions: {path}")


if __name__ == "__main__":
    generate()
