"""
RescueRoute command-line entry point: runs FIFO and greedy on one dataset and prints a report.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

Usage:
    python3 main.py                          # data/scale/small
    python3 main.py data/scenarios/starvation
    python3 main.py data/scale/medium --out report.txt

Educational prototype on simulated data. Not food-safety or operational advice.
"""

import argparse
import sys
from pathlib import Path

from rescueroute.report import build_report


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare FIFO and greedy urgency-first scheduling on a dataset folder.")
    parser.add_argument("folder", nargs="?", default="data/scale/small",
                        help="folder with donations, recipients, volunteers (.csv or .json); "
                             "default: data/scale/small")
    parser.add_argument("--out", help="also save the report to this file")
    args = parser.parse_args(argv)

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"Dataset folder not found: {folder}. "
              "Run `python3 data/scripts/generate_data.py` to create the sample data.", file=sys.stderr)
        return 1

    report = build_report(folder)
    print(report, end="")
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
        print(f"Report saved to {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
