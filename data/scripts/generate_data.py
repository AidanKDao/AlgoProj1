"""
Generate RescueRoute sample datasets in both CSV and JSON.

Usage (from the repo root):
    python data/scripts/generate_data.py

Writes:
    data/scale/<tiny|small|medium|large|xlarge>/   randomized datasets of increasing size
    data/scenarios/<name>/                         hand-built edge cases for tests and demos

Each dataset folder contains donations, recipients, and volunteers as both
.csv and .json with identical records. Random data uses a fixed seed, so
re-running the script reproduces the same files.

All times are integer minutes since the start of the simulation
(minute 0 = 8:00 AM, minute 720 = 8:00 PM).

This is AI generated code intended to provide a realistic simulation of a food rescue routing system input.
"""

import csv
import json
import random
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent

FOOD_TYPES = ["prepared_meals", "produce", "bakery", "dairy", "frozen", "canned_goods"]
AREAS = ["north", "south", "east", "west", "central"]

# Shelf life range in minutes, per food type (after the donation is ready)
SHELF_LIFE = {
    "prepared_meals": (45, 180),
    "dairy": (120, 360),
    "frozen": (90, 240),
    "bakery": (180, 600),
    "produce": (240, 720),
    "canned_goods": (1440, 4320),
}

DONOR_NAMES = [
    "Campus Dining Hall", "Titan Student Union Cafe", "Green Leaf Grocery", "Sunrise Bakery",
    "Harbor Catering Co.", "FreshMart", "Downtown Deli", "Oak Street Market", "Golden Crust Bakery",
    "Riverside Farmers Market", "Event Center Catering", "Corner Pantry Grocery", "Maple Cafe",
    "Valley Produce Wholesale", "Bright Morning Bagels",
]
RECIPIENT_NAMES = [
    "Community Shelter", "Eastside Food Pantry", "Hope Community Fridge", "Family Support Center",
    "Northside Youth Center", "Senior Meals Program", "Westside Pantry", "Central Soup Kitchen",
    "Harbor Outreach", "Southside Community Fridge", "New Start Shelter", "Unity Food Bank",
]

DONATION_FIELDS = ["donation_id", "donor_name", "food_type", "quantity",
                   "ready_time", "expiry_time", "pickup_area"]
RECIPIENT_FIELDS = ["recipient_id", "organization_name", "accepted_food_types",
                    "capacity", "closing_time", "dropoff_area"]
VOLUNTEER_FIELDS = ["volunteer_id", "vehicle_capacity", "maximum_pickups",
                    "availability_start", "availability_end", "pickup_area"]

# name -> (donations, recipients, volunteers)
SCALES = {
    "tiny": (8, 3, 3),
    "small": (25, 6, 6),
    "medium": (100, 20, 15),
    "large": (1000, 120, 90),
    "xlarge": (10000, 1000, 700),
}


# ---------- random generation ----------

def make_donations(rng: random.Random, n: int) -> list[dict]:
    donations = []
    for i in range(n):
        food = rng.choice(FOOD_TYPES)
        ready = rng.randrange(0, 600, 5)
        low, high = SHELF_LIFE[food]
        donations.append({
            "donation_id": f"D-{1001 + i}",
            "donor_name": rng.choice(DONOR_NAMES),
            "food_type": food,
            "quantity": rng.randint(5, 80),
            "ready_time": ready,
            "expiry_time": ready + rng.randrange(low, high + 1, 5),
            "pickup_area": rng.choice(AREAS),
        })
    return donations


def make_recipients(rng: random.Random, n: int) -> list[dict]:
    recipients = []
    for i in range(n):
        base = RECIPIENT_NAMES[i % len(RECIPIENT_NAMES)]
        name = base if i < len(RECIPIENT_NAMES) else f"{base} #{i // len(RECIPIENT_NAMES) + 1}"
        recipients.append({
            "recipient_id": f"R-{201 + i}",
            "organization_name": name,
            "accepted_food_types": sorted(rng.sample(FOOD_TYPES, rng.randint(2, 5))),
            "capacity": rng.randrange(50, 301, 10),
            "closing_time": rng.randrange(360, 721, 30),
            "dropoff_area": rng.choice(AREAS),
        })
    return recipients


def make_volunteers(rng: random.Random, n: int) -> list[dict]:
    volunteers = []
    for i in range(n):
        start = rng.randrange(0, 481, 30)
        volunteers.append({
            "volunteer_id": f"V-{301 + i}",
            "vehicle_capacity": rng.randrange(20, 121, 10),
            "maximum_pickups": rng.randint(2, 6),
            "availability_start": start,
            "availability_end": min(720, start + rng.randrange(120, 361, 30)),
            "pickup_area": rng.choice(AREAS),
        })
    return volunteers


# ---------- hand-built scenarios ----------

def d(did, donor, food, qty, ready, expiry, area):
    return dict(zip(DONATION_FIELDS, [did, donor, food, qty, ready, expiry, area]))


def r(rid, name, foods, cap, closing, area):
    return dict(zip(RECIPIENT_FIELDS, [rid, name, sorted(foods), cap, closing, area]))


def v(vid, cap, max_pickups, start, end, area):
    return dict(zip(VOLUNTEER_FIELDS, [vid, cap, max_pickups, start, end, area]))


SCENARIOS = {
    # One compatible donation, recipient, and volunteer: should be assigned.
    "normal_match": (
        [d("D-1001", "Campus Dining Hall", "prepared_meals", 30, 0, 90, "central")],
        [r("R-201", "Community Shelter", {"prepared_meals", "produce"}, 100, 600, "central")],
        [v("V-301", 50, 3, 0, 240, "central")],
    ),
    # D-1001 appears twice; validation should flag the second record.
    "duplicate_ids": (
        [d("D-1001", "Campus Dining Hall", "prepared_meals", 30, 0, 90, "central"),
         d("D-1001", "Sunrise Bakery", "bakery", 20, 30, 400, "north"),
         d("D-1002", "FreshMart", "produce", 25, 0, 480, "central")],
        [r("R-201", "Community Shelter", {"prepared_meals", "produce", "bakery"}, 200, 600, "central"),
         r("R-201", "Duplicate Pantry", {"produce"}, 100, 600, "north")],
        [v("V-301", 60, 4, 0, 480, "central"),
         v("V-301", 40, 2, 0, 480, "north")],
    ),
    # D-1001 is already expired at ready time; D-1002 has only 10 minutes left.
    "expired_donation": (
        [d("D-1001", "Downtown Deli", "prepared_meals", 20, 60, 60, "central"),
         d("D-1002", "Maple Cafe", "prepared_meals", 15, 0, 10, "central"),
         d("D-1003", "FreshMart", "produce", 25, 0, 480, "central")],
        [r("R-201", "Community Shelter", {"prepared_meals", "produce"}, 200, 600, "central")],
        [v("V-301", 60, 4, 0, 480, "central")],
    ),
    # No recipient accepts dairy.
    "no_compatible_food_type": (
        [d("D-1001", "Green Leaf Grocery", "dairy", 20, 0, 240, "east")],
        [r("R-201", "Eastside Food Pantry", {"produce", "canned_goods"}, 200, 600, "east"),
         r("R-202", "Hope Community Fridge", {"bakery"}, 100, 600, "east")],
        [v("V-301", 60, 3, 0, 480, "east")],
    ),
    # Donation is larger than any recipient's capacity.
    "insufficient_recipient_capacity": (
        [d("D-1001", "Event Center Catering", "prepared_meals", 150, 0, 120, "west")],
        [r("R-201", "Westside Pantry", {"prepared_meals"}, 80, 600, "west"),
         r("R-202", "New Start Shelter", {"prepared_meals"}, 100, 600, "west")],
        [v("V-301", 200, 3, 0, 480, "west")],
    ),
    # Recipient can take it, but no volunteer's vehicle can carry 90 units.
    "no_volunteer_capacity": (
        [d("D-1001", "Valley Produce Wholesale", "produce", 90, 0, 480, "south")],
        [r("R-201", "Southside Community Fridge", {"produce"}, 200, 600, "south")],
        [v("V-301", 40, 3, 0, 480, "south"),
         v("V-302", 60, 3, 0, 480, "south")],
    ),
    # Two donations, capacity for only one of them.
    "competing_capacity": (
        [d("D-1001", "Sunrise Bakery", "bakery", 40, 0, 400, "north"),
         d("D-1002", "Golden Crust Bakery", "bakery", 40, 0, 300, "north")],
        [r("R-201", "Northside Youth Center", {"bakery"}, 50, 600, "north")],
        [v("V-301", 50, 4, 0, 480, "north")],
    ),
    # FIFO assigns 1, greedy assigns 2:
    #   FIFO:   D-1001 (arrived first) takes R-201's only capacity; D-1002 is
    #           prepared meals and R-202 does not accept those -> unassigned.
    #   Greedy: D-1002 expires sooner, takes R-201; D-1001 (produce) then goes to R-202.
    "fifo_vs_greedy_differ": (
        [d("D-1001", "FreshMart", "produce", 30, 0, 600, "central"),
         d("D-1002", "Campus Dining Hall", "prepared_meals", 30, 0, 90, "central")],
        [r("R-201", "Community Shelter", {"prepared_meals", "produce"}, 30, 600, "central"),
         r("R-202", "Eastside Food Pantry", {"produce"}, 50, 600, "central")],
        [v("V-301", 40, 1, 0, 480, "central"),
         v("V-302", 40, 1, 0, 480, "central")],
    ),
    # Starvation discussion: a steady stream of short-shelf-life meals keeps
    # jumping ahead of D-1001 (canned goods, arrived first) under urgency-first,
    # and the lone volunteer runs out of pickups before reaching it.
    "starvation": (
        [d("D-1001", "Corner Pantry Grocery", "canned_goods", 20, 0, 2880, "central")]
        + [d(f"D-{1002 + i}", "Campus Dining Hall", "prepared_meals", 10, i * 20, i * 20 + 60, "central")
           for i in range(4)],
        [r("R-201", "Central Soup Kitchen", {"prepared_meals", "canned_goods"}, 200, 720, "central")],
        [v("V-301", 40, 4, 0, 720, "central")],
    ),
    # Headers only / empty lists.
    "empty": ([], [], []),
}


# ---------- writers ----------

def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            # Sets/lists are stored in one cell, separated by semicolons
            writer.writerow({k: ";".join(val) if isinstance(val, list) else val
                             for k, val in row.items()})


def write_json(path: Path, rows: list[dict]) -> None:
    path.write_text(json.dumps(rows, indent=2) + "\n")


def write_dataset(folder: Path, donations, recipients, volunteers) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    for name, fields, rows in [("donations", DONATION_FIELDS, donations),
                               ("recipients", RECIPIENT_FIELDS, recipients),
                               ("volunteers", VOLUNTEER_FIELDS, volunteers)]:
        write_csv(folder / f"{name}.csv", fields, rows)
        write_json(folder / f"{name}.json", rows)


def main() -> None:
    for sub in ("scale", "scenarios"):
        shutil.rmtree(DATA_DIR / sub, ignore_errors=True)

    for name, (n_don, n_rec, n_vol) in SCALES.items():
        rng = random.Random(335)
        write_dataset(DATA_DIR / "scale" / name,
                      make_donations(rng, n_don), make_recipients(rng, n_rec), make_volunteers(rng, n_vol))
        print(f"scale/{name}: {n_don} donations, {n_rec} recipients, {n_vol} volunteers")

    for name, (donations, recipients, volunteers) in SCENARIOS.items():
        write_dataset(DATA_DIR / "scenarios" / name, donations, recipients, volunteers)
        print(f"scenarios/{name}")


if __name__ == "__main__":
    main()
