"""
Tests for the command-line report (main.py and rescueroute/report.py).

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md
"""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

import main
from rescueroute.report import build_report
from tests.helpers import SCENARIOS, ensure_sample_data, load_scenario


def setUpModule():
    ensure_sample_data()


# run_main: calls main.main with the given arguments and returns (exit code, printed text, stderr).
def run_main(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main.main(list(args))
    return code, out.getvalue(), err.getvalue()


class TestReport(unittest.TestCase):

    # The brief requires an explanation for every donation, from both strategies. Each donation
    # ID must appear in a sentence in each section, not only in a table.
    def test_every_donation_has_an_explanation_in_both_strategies(self):
        donations, _, _, _ = load_scenario("starvation")
        report = build_report(SCENARIOS / "starvation")
        fifo_part, greedy_part = report.split("B. GREEDY URGENCY-FIRST")
        for donation_id in donations:
            with self.subTest(donation_id):
                self.assertIn(f"Donation {donation_id} ", fifo_part)
                self.assertIn(f"Donation {donation_id} ", greedy_part)

    # Greedy reorders donations, and the report lists each strategy in the order it processed them.
    def test_processing_order_shows_the_reordering(self):
        report = build_report(SCENARIOS / "starvation")
        self.assertIn("Processing order: D-1001, D-1002, D-1003, D-1004, D-1005", report)   # FIFO
        self.assertIn("Processing order: D-1002, D-1003, D-1004, D-1005, D-1001", report)   # greedy

    # Validation errors are printed before any strategy results, and the run still continues.
    def test_validation_errors_come_before_results(self):
        report = build_report(SCENARIOS / "duplicate_ids")
        self.assertIn("duplicate donation_id", report)
        self.assertLess(report.index("VALIDATION"), report.index("A. FIFO BASELINE"))
        self.assertLess(report.index("duplicate donation_id"), report.index("A. FIFO BASELINE"))
        self.assertIn("METRICS", report)

    # The metrics table and the FIFO-vs-greedy differences are included.
    def test_report_has_metrics_and_comparison(self):
        report = build_report(SCENARIOS / "fifo_vs_greedy_differ")
        self.assertIn("Urgent rescue rate", report)
        self.assertIn("Difference in assigned donations: +1", report)
        self.assertIn("Greedy rescued more food", report)

    # Empty input must not crash and must say there is nothing to process.
    def test_empty_dataset(self):
        report = build_report(SCENARIOS / "empty")
        self.assertIn("No donations to process.", report)
        self.assertIn("No problems found.", report)

    # JSON-only dataset folders work: a temporary folder with just .json copies of a scenario.
    def test_json_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("donations", "recipients", "volunteers"):
                (Path(tmp) / f"{name}.json").write_text((SCENARIOS / "normal_match" / f"{name}.json").read_text())
            self.assertIn("ASSIGNED to R-201 with V-301", build_report(Path(tmp)))

    # The report states plainly that this is a prototype on simulated data.
    def test_disclaimer_is_present(self):
        self.assertIn("simulated data", build_report(SCENARIOS / "normal_match"))


class TestMain(unittest.TestCase):

    def test_prints_report_and_returns_zero(self):
        code, out, _ = run_main(str(SCENARIOS / "normal_match"))
        self.assertEqual(code, 0)
        self.assertIn("A. FIFO BASELINE", out)

    # --out saves the same report to a file.
    def test_out_saves_the_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "report.txt"
            code, out, _ = run_main(str(SCENARIOS / "normal_match"), "--out", str(target))
            self.assertEqual(code, 0)
            self.assertEqual(target.read_text(encoding="utf-8"), build_report(SCENARIOS / "normal_match"))

    # A missing folder gives a clear message and a non-zero exit code, not a traceback.
    def test_missing_folder_is_a_clear_error(self):
        code, _, err = run_main("data/scenarios/does_not_exist")
        self.assertEqual(code, 1)
        self.assertIn("not found", err)


if __name__ == "__main__":
    unittest.main()
