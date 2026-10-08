"""Local, dependency-free dining estimator. All bundled observations are synthetic."""
import csv
from pathlib import Path


def quantile(values, q):
    values = sorted(values)
    position = (len(values) - 1) * q
    left = int(position)
    right = min(left + 1, len(values) - 1)
    return values[left] + (values[right] - values[left]) * (position - left)


class DurationModel:
    """Empirical conditional duration model; no neural network or accelerator."""
    def __init__(self, path):
        with Path(path).open(encoding="utf-8", newline="") as file:
            self.rows = list(csv.DictReader(file))
        self.buckets = {}
        for row in self.rows:
            key = (row["meal"], int(row["party"]))
            self.buckets.setdefault(key, []).append(float(row["duration_min"]))

    def estimate(self, meal, party, elapsed=0, q=0.5):
        durations = self.buckets[(meal, party)]
        # Condition on still being seated, instead of subtracting elapsed from
        # an unconditional average (which incorrectly produces zero for late diners).
        residuals = [d - elapsed for d in durations if d > elapsed]
        if len(residuals) < 5:
            # Explicit heuristic for an out-of-distribution, unusually long meal.
            return {"minutes": 10.0 if q == 0.5 else 20.0,
                    "support": len(residuals), "fallback": True}
        return {"minutes": quantile(residuals, q),
                "support": len(residuals), "fallback": False}


def seating_time(restaurant, party, arrival, model, q):
    """Strict FIFO; one party per table; no merging, sharing, or new arrivals."""
    tables = restaurant["tables"]
    if not any(t["capacity"] >= party for t in tables):
        return None
    free = []
    for table in tables:
        if table["party"]:
            remaining = model.estimate(restaurant["meal"], table["party"],
                                       table["elapsed"], q)["minutes"]
            free.append(remaining + restaurant["cleanup"])
        else:
            free.append(0.0)
    front = 0.0
    # Existing queued groups arrived before t=0. The user joins at arrival.
    for index, size in enumerate(restaurant["queue"] + [party]):
        eligible = [i for i, t in enumerate(tables) if t["capacity"] >= size]
        if not eligible:
            return None  # Strict FIFO blocked by a group we cannot seat.
        earliest = max(front, min(free[i] for i in eligible))
        if index == len(restaurant["queue"]):
            earliest = max(earliest, arrival)
        # Prefer the smallest table already available at this seating time.
        chosen = min((i for i in eligible if free[i] <= earliest + 1e-9),
                     key=lambda i: (tables[i]["capacity"], i))
        front = earliest
        if index == len(restaurant["queue"]):
            return earliest
        free[chosen] = earliest + model.estimate(restaurant["meal"], size, q=q)["minutes"] + restaurant["cleanup"]


def travel(distance_m, mode):
    # Route distances are manually configured demo distances, not map routes.
    speed = 80 if mode == "walk" else 240
    overhead = 0 if mode == "walk" else 2  # Unlock/park overhead per leg.
    return distance_m / speed + overhead


def recommend(restaurant, options, model):
    outbound = travel(restaurant["outbound_m"], options["out_mode"])
    inbound = travel(restaurant["return_m"], options["back_mode"])
    result = {"id": restaurant["id"], "name": restaurant["name"],
              "meal": restaurant["meal"], "queue": restaurant["queue"],
              "outbound_m": restaurant["outbound_m"], "return_m": restaurant["return_m"],
              "tables": [], "scenarios": {}}
    for table in restaurant["tables"]:
        result["tables"].append({**table,
            "remaining": model.estimate(restaurant["meal"], table["party"], table["elapsed"])
            if table["party"] else None})
    for name, q in [("typical", .5), ("cautious", .8)]:
        seat = seating_time(restaurant, options["party"], outbound, model, q)
        if seat is None:
            result["scenarios"][name] = None
            continue
        dining = model.estimate(restaurant["meal"], options["party"], q=q)["minutes"]
        total = seat + dining + inbound
        result["scenarios"][name] = {
            "outbound": outbound, "wait": max(0, seat - outbound),
            "dining": dining, "inbound": inbound, "total": total,
            "margin": options["budget"] - options["buffer"] - total,
            "return_at": options["now_min"] + total}
    typical = result["scenarios"]["typical"]
    cautious = result["scenarios"]["cautious"]
    result["status"] = ("unavailable" if typical is None else
                         "on-time" if cautious["margin"] >= 0 else
                         "tight" if typical["margin"] >= 0 else "late")
    return result


def validate_options(raw):
    def integer(key, low, high):
        value = raw[key]
        if type(value) is not int or not low <= value <= high:
            raise ValueError(f"{key} must be an integer from {low} to {high}.")
        return value
    options = {"party": integer("party", 1, 6),
               "buffer": integer("buffer", 0, 30),
               "now_min": integer("now_min", 0, 1439),
               "class_min": integer("class_min", 0, 1439)}
    options["budget"] = options["class_min"] - options["now_min"]
    if options["budget"] <= 0:
        raise ValueError("Class must start after departure on the same day.")
    for key in ("out_mode", "back_mode"):
        if raw.get(key) not in ("walk", "bike"):
            raise ValueError("Travel mode must be walk or bike.")
        options[key] = raw[key]
    return options
