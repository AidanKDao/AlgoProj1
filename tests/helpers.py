"""
Shared helpers for the RescueRoute tests.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by AidanDao, see docs/TOOLS_AND_SOURCES.md

The loader and FIFO scheduler are written by teammates and do not exist yet, so
this file is the ONE place that states the interface the tests assume. If the
real signatures differ, change them here and the tests keep working.

Assumed interface:
    rescueroute.loader.load_donations(path)  -> (dict[str, Donation],  list[str])
    rescueroute.loader.load_recipients(path) -> (dict[str, Recipient], list[str])
    rescueroute.loader.load_volunteers(path) -> (dict[str, Volunteer], list[str])
        Each returns (records keyed by ID, list of human-readable validation errors).
        Records that fail validation are left out of the dict.
    rescueroute.strategies.fifo.run_fifo(donations, recipients, volunteers)
        -> list[Assignment], exactly one per donation, in arrival order.
        Unassigned donations have status Status.UNASSIGNED and recipient_id/volunteer_id
        of None; every Assignment has a non-empty decision_reason.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCENARIOS = ROOT / "data" / "scenarios"


def ensure_sample_data() -> None:
    """data/scenarios is gitignored, so generate it if a fresh clone lacks it."""
    if not SCENARIOS.exists():
        subprocess.run([sys.executable, str(ROOT / "data" / "scripts" / "generate_data.py")],
                       check=True, cwd=ROOT)


def load_scenario(name: str, ext: str = "csv"):
    """Load a hand-built scenario folder. Returns (donations, recipients, volunteers, errors)
    where errors maps "donations"/"recipients"/"volunteers" to their validation error lists."""
    from rescueroute import loader

    folder = SCENARIOS / name
    donations, d_err = loader.load_donations(folder / f"donations.{ext}")
    recipients, r_err = loader.load_recipients(folder / f"recipients.{ext}")
    volunteers, v_err = loader.load_volunteers(folder / f"volunteers.{ext}")
    errors = {"donations": d_err, "recipients": r_err, "volunteers": v_err}
    return donations, recipients, volunteers, errors


def run_fifo_scenario(name: str, ext: str = "csv"):
    """Load a scenario and run FIFO on it. Returns {donation_id: Assignment}."""
    from rescueroute.strategies.fifo import run_fifo

    donations, recipients, volunteers, _ = load_scenario(name, ext)
    return {a.donation_id: a for a in run_fifo(donations, recipients, volunteers)}
