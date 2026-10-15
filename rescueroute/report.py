"""
Builds the FIFO-vs-greedy text report that main.py prints.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

The report follows docs/project_logic/002 ("Validation and output"): validation errors first,
then every donation's explanation in the order each strategy processed it, then the metrics
table and the FIFO-vs-greedy differences. This is an educational prototype on simulated data.
"""

from pathlib import Path

from rescueroute.loader import load_donations, load_recipients, load_volunteers
from rescueroute.metrics import calculate_metrics
from rescueroute.models import Status
from rescueroute.strategies.fifo import run_fifo
from rescueroute.strategies.greedy import run_greedy

# Metric key -> label, in the order the table shows them.
METRIC_LABELS = {
    "total_donations": "Total donations",
    "assigned": "Assigned",
    "unassigned": "Unassigned",
    "total_food": "Total food units",
    "rescued_food": "Food rescued",
    "assignment_rate": "Assignment rate (%)",
    "food_rescue_rate": "Food rescue rate (%)",
    "food_at_risk": "Food at risk",
    "urgent_donations": "Urgent donations",
    "urgent_assigned": "Urgent assigned",
    "urgent_rescue_rate": "Urgent rescue rate (%)",
    "recipient_utilization": "Recipient utilization (%)",
    "volunteer_utilization": "Volunteer utilization (%)",
}


# find_data_file: the dataset folders hold donations.csv or donations.json. Prefer CSV, fall
# back to JSON, and return the CSV path if neither exists so the loader reports "file not found".
def find_data_file(folder: Path, name: str) -> Path:
    for extension in ("csv", "json"):
        path = folder / f"{name}.{extension}"
        if path.exists():
            return path
    return folder / f"{name}.csv"


# load_dataset: loads all three files and returns the records plus every validation error.
def load_dataset(folder: Path):
    donations, d_errors = load_donations(find_data_file(folder, "donations"))
    recipients, r_errors = load_recipients(find_data_file(folder, "recipients"))
    volunteers, v_errors = load_volunteers(find_data_file(folder, "volunteers"))
    return donations, recipients, volunteers, d_errors + r_errors + v_errors


# strategy_section: the text for one strategy. First the processing order, then one entry per
# donation (in that same order) with its status, trip times, and full explanation sentence.
def strategy_section(title: str, rule: str, assignments: list) -> list[str]:
    lines = [title, rule, ""]
    if not assignments:
        return lines + ["  No donations to process.", ""]
    lines.append("Processing order: " + ", ".join(a.donation_id for a in assignments))
    lines.append("")
    for step, a in enumerate(assignments, start=1):
        if a.status == Status.ASSIGNED:
            summary = f"ASSIGNED to {a.recipient_id} with {a.volunteer_id}, minutes {a.scheduled_time_start}-{a.scheduled_time_end}"
        else:
            summary = "UNASSIGNED"
        lines.append(f"  {step}. {a.donation_id}: {summary}")
        lines.append(f"     {a.decision_reason}")
    lines.append("")
    return lines


# metrics_section: the metrics table (FIFO and greedy side by side) and the differences.
def metrics_section(fifo: dict, greedy: dict) -> list[str]:
    lines = ["METRICS", "-" * 55, f"{'Metric':<27}{'FIFO':>12}{'Greedy':>12}", "-" * 55]
    for key, label in METRIC_LABELS.items():
        lines.append(f"{label:<27}{fifo[key]:>12}{greedy[key]:>12}")
    lines += ["", "FIFO VS GREEDY"]
    lines.append(f"Difference in assigned donations: {greedy['assigned'] - fifo['assigned']:+d}")
    rescued = greedy["rescued_food"] - fifo["rescued_food"]
    lines.append(f"Difference in food rescued: {rescued:+d} units")
    lines.append(f"Difference in urgent rescue rate: {greedy['urgent_rescue_rate'] - fifo['urgent_rescue_rate']:+.2f} points")
    if rescued > 0:
        lines.append("Greedy rescued more food on this dataset.")
    elif rescued < 0:
        lines.append("FIFO rescued more food on this dataset.")
    else:
        lines.append("Both strategies rescued the same amount of food.")
    return lines


# build_report: runs both strategies on the SAME loaded data and returns the whole report as text.
def build_report(folder: Path) -> str:
    donations, recipients, volunteers, errors = load_dataset(folder)

    lines = ["RESCUEROUTE: FIFO VS GREEDY URGENCY-FIRST",
             "Educational prototype on simulated data. Not food-safety or operational advice.",
             f"Dataset: {folder}", ""]

    # Validation errors come first. Invalid records were dropped by the loader; the run continues.
    lines.append("VALIDATION")
    if errors:
        lines.append(f"{len(errors)} problem(s) found. Invalid records were skipped; the rest were processed.")
        lines += [f"  - {error}" for error in errors]
    else:
        lines.append("No problems found.")
    lines.append("")

    # Both strategies get the same loaded data. Each builds its own fresh capacity state.
    fifo_assignments = run_fifo(donations, recipients, volunteers)
    greedy_assignments = run_greedy(donations, recipients, volunteers)

    lines += strategy_section(
        "A. FIFO BASELINE",
        "Rule: donations are processed in arrival order; each takes the first feasible recipient and volunteer.",
        fifo_assignments)
    lines += strategy_section(
        "B. GREEDY URGENCY-FIRST",
        "Rule: earliest expiry first, then fewest compatible recipients, then larger quantity, then earlier arrival.",
        greedy_assignments)

    fifo_metrics = calculate_metrics(donations, fifo_assignments, recipients, volunteers)
    greedy_metrics = calculate_metrics(donations, greedy_assignments, recipients, volunteers)
    lines += metrics_section(fifo_metrics, greedy_metrics)
    return "\n".join(lines) + "\n"
