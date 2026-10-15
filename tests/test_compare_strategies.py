
"""Tests for the FIFO vs Greedy comparison program.

These tests verify the comparison works using a small,
temporary dataset and handles missing files correctly.
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from io import StringIO
from contextlib import redirect_stdout

from compare_strategies import compare_strategies


class TestStrategyComparison(unittest.TestCase):

    def test_small_dataset_comparison(self):
        """Both strategies should process the same valid sample data."""

        # Create a temporary folder for our test files.
        # It is automatically deleted when the test finishes.
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)

            # Create one donation with enough time before expiration.
            (folder / "donations.csv").write_text(
                "donation_id,donor_name,food_type,quantity,"
                "ready_time,expiry_time,pickup_area\n"
                "D-1,Campus Dining,produce,10,0,300,north\n",
                encoding="utf-8"
            )

            # Create a recipient who can accept this donation.
            (folder / "recipients.csv").write_text(
                "recipient_id,organization_name,accepted_food_types,"
                "capacity,closing_time,dropoff_area\n"
                "R-1,Food Bank,produce,100,500,north\n",
                encoding="utf-8"
            )

            # Create a volunteer available for the delivery.
            (folder / "volunteers.csv").write_text(
                "volunteer_id,vehicle_capacity,maximum_pickups,"
                "availability_start,availability_end,pickup_area\n"
                "V-1,50,2,0,500,north\n",
                encoding="utf-8"
            )

            # Capture the comparison report.
            output = StringIO()

            with redirect_stdout(output):
                result = compare_strategies(folder)

            printed_output = output.getvalue()

            # Both strategies should run successfully.
            self.assertEqual(result, 0)

            # Verify the report contains the expected sections.
            self.assertIn("FIFO VS GREEDY", printed_output)
            self.assertIn("Food rescued", printed_output)
            self.assertIn("Assignment rate", printed_output)
            self.assertIn("COMPARISON SUMMARY", printed_output)
            self.assertIn("Food at risk", printed_output)
            self.assertIn("Urgent rescue rate", printed_output)
            self.assertIn("Recipient utilization", printed_output)
            self.assertIn("Volunteer utilization", printed_output)

            # Both should rescue the single valid donation.
            self.assertIn(
                "Difference in assigned donations: +0",
                printed_output
            )
            self.assertIn(
                "Difference in food rescued: +0 units",
                printed_output
            )

    def test_missing_dataset(self):
        """Missing input files should produce a readable error."""

        # Create an empty temporary folder with no CSV files.
        with TemporaryDirectory() as temp_dir:
            folder = Path(temp_dir)
            output = StringIO()

            with redirect_stdout(output):
                result = compare_strategies(folder)

            printed_output = output.getvalue()

            # The program should report an error without crashing.
            self.assertEqual(result, 1)
            self.assertIn(
                "Dataset contains validation errors",
                printed_output
            )
            self.assertIn("file not found", printed_output)


if __name__ == "__main__":
    unittest.main()
