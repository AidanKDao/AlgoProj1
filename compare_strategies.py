
"""Compare FIFO and Greedy scheduling strategies for RescueRoute.

This program loads the same dataset for both strategies,
runs them independently, and displays their performance metrics.
"""

import sys
from pathlib import Path

from rescueroute.loader import (
    load_donations,
    load_recipients,
    load_volunteers,
)
from rescueroute.strategies.fifo import run_fifo
from rescueroute.strategies.greedy import run_greedy
from rescueroute.metrics import calculate_metrics


def compare_strategies(folder):
    """Run both strategies on the same dataset and compare results."""

    # Step 1: Load donations, recipients, and volunteers.
    # The loader returns valid records and any validation errors.
    donations, d_errors = load_donations(folder / "donations.csv")
    recipients, r_errors = load_recipients(folder / "recipients.csv")
    volunteers, v_errors = load_volunteers(folder / "volunteers.csv")

    # Step 2: Check for invalid data before running the algorithms.
    errors = d_errors + r_errors + v_errors

    if errors:
        print("Dataset contains validation errors:")
        for error in errors:
            print(f"- {error}")
        return 1

    # Step 3: Run FIFO and calculate its performance metrics.
    # FIFO processes donations based on arrival order.
    fifo_assignments = run_fifo(donations, recipients, volunteers)
    fifo_metrics = calculate_metrics(donations, fifo_assignments)

    # Step 4: Run Greedy and calculate its performance metrics.
    # Greedy prioritizes donations using the team's greedy rules.
    # Each strategy creates its own capacity tracker, so the
    # results from FIFO do not affect Greedy.
    greedy_assignments = run_greedy(donations, recipients, volunteers)
    greedy_metrics = calculate_metrics(donations, greedy_assignments)

    # Step 5: Display results side by side.
    print("\nRESCUEROUTE - FIFO VS GREEDY")
    print(f"Dataset: {folder}")
    print("-" * 55)
    print(f"{'Metric':<25} {'FIFO':>12} {'Greedy':>12}")
    print("-" * 55)

    labels = {
        "total_donations": "Total donations",
        "assigned": "Assigned",
        "unassigned": "Unassigned",
        "total_food": "Total food units",
        "rescued_food": "Food rescued",
        "assignment_rate": "Assignment rate (%)",
        "food_rescue_rate": "Food rescue rate (%)",
    }

    for key, label in labels.items():
        print(
            f"{label:<25} "
            f"{fifo_metrics[key]:>12} "
            f"{greedy_metrics[key]:>12}"
        )

    # Step 6: Calculate the difference between both strategies.
    # Positive differences mean Greedy rescued more than FIFO.
    rescued_difference = (
        greedy_metrics["rescued_food"] - fifo_metrics["rescued_food"]
    )

    assignment_difference = (
        greedy_metrics["assigned"] - fifo_metrics["assigned"]
    )

    print("\nCOMPARISON SUMMARY")
    print(f"Difference in assigned donations: {assignment_difference:+d}")
    print(f"Difference in food rescued: {rescued_difference:+d} units")

    if rescued_difference > 0:
        print("Greedy rescued more food on this dataset.")
    elif rescued_difference < 0:
        print("FIFO rescued more food on this dataset.")
    else:
        print("Both strategies rescued the same amount of food.")

    return 0


if __name__ == "__main__":

    # Use the small dataset by default.
    # Users can also pass a different dataset folder.
    folder = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "data/scale/small"
    )

    sys.exit(compare_strategies(folder))
