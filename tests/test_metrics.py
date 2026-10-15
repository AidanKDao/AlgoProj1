
"""Tests for RescueRoute performance metrics.

These tests verify that our metrics are calculated correctly
before we use them to compare FIFO and Greedy.
"""

import unittest
from types import SimpleNamespace

from rescueroute.models import Status
from rescueroute.metrics import calculate_metrics


class TestMetrics(unittest.TestCase):

    def test_mixed_assignments(self):
        """Check metrics when some donations are assigned and others are not."""

        # Three donations containing 60 total units of food.
        donations = {
            "D1": SimpleNamespace(quantity=10),
            "D2": SimpleNamespace(quantity=20),
            "D3": SimpleNamespace(quantity=30),
        }

        # D1 and D3 are assigned, while D2 is unassigned.
        assignments = [
            SimpleNamespace(donation_id="D1", status=Status.ASSIGNED),
            SimpleNamespace(donation_id="D2", status=Status.UNASSIGNED),
            SimpleNamespace(donation_id="D3", status=Status.ASSIGNED),
        ]

        results = calculate_metrics(donations, assignments)

        # Verify successful assignments and food rescued.
        self.assertEqual(results["total_donations"], 3)
        self.assertEqual(results["assigned"], 2)
        self.assertEqual(results["unassigned"], 1)
        self.assertEqual(results["total_food"], 60)
        self.assertEqual(results["rescued_food"], 40)
        self.assertEqual(results["assignment_rate"], 66.67)
        self.assertEqual(results["food_rescue_rate"], 66.67)

    def test_empty_donations(self):
        """An empty dataset should return zero instead of crashing."""

        results = calculate_metrics({}, [])

        self.assertEqual(results["total_donations"], 0)
        self.assertEqual(results["assigned"], 0)
        self.assertEqual(results["rescued_food"], 0)
        self.assertEqual(results["assignment_rate"], 0.0)
        self.assertEqual(results["food_rescue_rate"], 0.0)

    def test_duplicate_assignments(self):
        """The same donation should never be counted twice."""

        donations = {
            "D1": SimpleNamespace(quantity=10),
            "D2": SimpleNamespace(quantity=20),
        }

        # D1 accidentally appears twice in the results.
        assignments = [
            SimpleNamespace(donation_id="D1", status=Status.ASSIGNED),
            SimpleNamespace(donation_id="D1", status=Status.ASSIGNED),
        ]

        results = calculate_metrics(donations, assignments)

        # D1 should count only once.
        self.assertEqual(results["assigned"], 1)
        self.assertEqual(results["rescued_food"], 10)
        self.assertEqual(results["assignment_rate"], 50.0)


if __name__ == "__main__":
    unittest.main()
