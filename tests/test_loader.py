"""
Loader validation tests: bad field values are reported with record, field, and reason.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md
"""

import tempfile
import unittest
from pathlib import Path

from rescueroute import loader
from tests.helpers import ensure_sample_data, load_scenario

HEADER = "donation_id,donor_name,food_type,quantity,ready_time,expiry_time,pickup_area\n"


def setUpModule():
    ensure_sample_data()


def load_donation_rows(*rows: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "donations.csv"
        path.write_text(HEADER + "".join(r + "\n" for r in rows))
        return loader.load_donations(path)


class TestLoaderValidation(unittest.TestCase):

    def test_empty_scenario_loads_nothing_without_errors(self):
        donations, recipients, volunteers, errors = load_scenario("empty")
        self.assertEqual((donations, recipients, volunteers), ({}, {}, {}))
        self.assertEqual(errors, {"donations": [], "recipients": [], "volunteers": []})

    def test_csv_and_json_load_identically(self):
        self.assertEqual(load_scenario("starvation", "csv")[:3], load_scenario("starvation", "json")[:3])

    def test_values_are_converted_and_arrival_order_assigned(self):
        donations, _ = load_donation_rows("D-1,A,dairy,10,0,60,north", "D-2,B,produce,5,0,90,south")
        self.assertEqual(donations["D-1"].quantity, 10)
        self.assertEqual([d.arrival_order for d in donations.values()], [0, 1])

    def test_bad_values_are_reported_and_record_skipped(self):
        donations, errors = load_donation_rows(
            "D-1,A,candy,10,0,60,north",       # unknown food type
            "D-2,A,dairy,-5,0,60,north",       # negative quantity
            "D-3,A,dairy,abc,0,60,north",      # non-numeric quantity
            "D-4,A,dairy,10,50,20,north",      # expiry before ready
            "D-5,A,dairy,10,0,60,mars",        # unknown area
            "D-6,A,dairy,10,0,60,north",       # valid
        )
        self.assertEqual(list(donations), ["D-6"])
        for donation_id, word in [("D-1", "food_type"), ("D-2", "quantity"), ("D-3", "quantity"),
                                  ("D-4", "expiry_time"), ("D-5", "pickup_area")]:
            with self.subTest(donation_id):
                self.assertTrue(any(donation_id in e and word in e for e in errors), errors)

    def test_missing_file_is_an_error_not_a_crash(self):
        records, errors = loader.load_donations("does_not_exist.csv")
        self.assertEqual(records, {})
        self.assertIn("not found", errors[0])


if __name__ == "__main__":
    unittest.main()
