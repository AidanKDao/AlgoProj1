"""
Loader validation tests: bad field values are reported with record, field, and reason.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

How these tests work: each test method (named test_...) sets up some input, runs the loader,
then uses assert methods to check the result. If an assert is false, that test fails.
    assertEqual(a, b)   passes if a == b
    assertIn(x, y)      passes if x is inside y (for example, a word inside a message)
    assertTrue(x)       passes if x is true
"""

import tempfile
import unittest
from pathlib import Path

from rescueroute import loader
from tests.helpers import ensure_sample_data, load_scenario

# The first line of a donations CSV file. Tests add rows underneath it.
HEADER = "donation_id,donor_name,food_type,quantity,ready_time,expiry_time,pickup_area\n"


# setUpModule: unittest runs this once before any test in the file. It makes sure the sample
# data in data/scenarios/ exists, because that folder is not stored in git.
def setUpModule():
    ensure_sample_data()


# load_donation_rows: a helper (not a test) that lets a test write its own donation rows.
# It writes the rows to a temporary CSV file, loads it with the real loader, and returns
# (donations, errors). *rows means "any number of row strings". The temporary folder is
# deleted automatically when the `with` block ends.
def load_donation_rows(*rows: str):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "donations.csv"
        path.write_text(HEADER + "".join(r + "\n" for r in rows))
        return loader.load_donations(path)


# A test class groups related tests. unittest runs every method starting with "test".
class TestLoaderValidation(unittest.TestCase):

    # Empty input: header-only CSVs and empty JSON lists should load as empty dicts, and an
    # empty file is not an error, so every error list should be empty too.
    def test_empty_scenario_loads_nothing_without_errors(self):
        donations, recipients, volunteers, errors = load_scenario("empty")
        self.assertEqual((donations, recipients, volunteers), ({}, {}, {}))
        self.assertEqual(errors, {"donations": [], "recipients": [], "volunteers": []})

    # The same data in CSV and in JSON must produce identical records. [:3] takes just the
    # first three items (donations, recipients, volunteers) and ignores the errors.
    def test_csv_and_json_load_identically(self):
        self.assertEqual(load_scenario("starvation", "csv")[:3], load_scenario("starvation", "json")[:3])

    # Conversion: the CSV text "10" must become the number 10, and arrival_order must come
    # from row position (first row 0, second row 1). `_` ignores the errors we don't need.
    def test_values_are_converted_and_arrival_order_assigned(self):
        donations, _ = load_donation_rows("D-1,A,dairy,10,0,60,north", "D-2,B,produce,5,0,90,south")
        self.assertEqual(donations["D-1"].quantity, 10)
        self.assertEqual([d.arrival_order for d in donations.values()], [0, 1])

    # Bad data: five rows each break one rule and one row is valid. Only the valid row may
    # load, and every bad row must have an error that names its ID and the bad field.
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
        # For each bad ID, check that some error message mentions both the ID and the field.
        # subTest reports each one separately, so a failure says which ID broke.
        for donation_id, word in [("D-1", "food_type"), ("D-2", "quantity"), ("D-3", "quantity"),
                                  ("D-4", "expiry_time"), ("D-5", "pickup_area")]:
            with self.subTest(donation_id):
                self.assertTrue(any(donation_id in e and word in e for e in errors), errors)

    # A missing file must give back an empty dict and an error message, not crash the program.
    def test_missing_file_is_an_error_not_a_crash(self):
        records, errors = loader.load_donations("does_not_exist.csv")
        self.assertEqual(records, {})
        self.assertIn("not found", errors[0])


# Lets you run this one file directly with: python3 tests/test_loader.py
if __name__ == "__main__":
    unittest.main()
