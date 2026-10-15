"""Tests for RescueRoute performance metrics.

These tests verify that our metrics are calculated correctly
before we use them to compare FIFO and Greedy.

AI-assisted: Claude Code, requested by AidanKDao (tests for the new metrics and
the updated calculate_metrics signature), see docs/TOOLS_AND_SOURCES.md
"""

import unittest
from types import SimpleNamespace

from rescueroute.models import Status
from rescueroute.metrics import calculate_metrics


def donation(donation_id, quantity, expiry_time=100, arrival_order=0):
    """A minimal stand-in for a Donation with only the fields metrics read."""
    return SimpleNamespace(
        donation_id=donation_id,
        quantity=quantity,
        expiry_time=expiry_time,
        arrival_order=arrival_order,
    )


def assigned(donation_id):
    return SimpleNamespace(donation_id=donation_id, status=Status.ASSIGNED)


def unassigned(donation_id):
    return SimpleNamespace(donation_id=donation_id, status=Status.UNASSIGNED)


def recipient(capacity):
    return SimpleNamespace(capacity=capacity)


def volunteer(vehicle_capacity, maximum_pickups):
    return SimpleNamespace(
        vehicle_capacity=vehicle_capacity, maximum_pickups=maximum_pickups
    )


class TestMetrics(unittest.TestCase):

    def test_mixed_assignments(self):
        """Check metrics when some donations are assigned and others are not."""

        # Three donations containing 60 total units of food.
        donations = {
            "D1": donation("D1", 10),
            "D2": donation("D2", 20),
            "D3": donation("D3", 30),
        }

        # D1 and D3 are assigned, while D2 is unassigned.
        assignments = [assigned("D1"), unassigned("D2"), assigned("D3")]

        results = calculate_metrics(donations, assignments, {}, {})

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

        results = calculate_metrics({}, [], {}, {})

        self.assertEqual(results["total_donations"], 0)
        self.assertEqual(results["assigned"], 0)
        self.assertEqual(results["rescued_food"], 0)
        self.assertEqual(results["assignment_rate"], 0.0)
        self.assertEqual(results["food_rescue_rate"], 0.0)
        self.assertEqual(results["food_at_risk"], 0)
        self.assertEqual(results["urgent_donations"], 0)
        self.assertEqual(results["urgent_rescue_rate"], 0.0)
        self.assertEqual(results["recipient_utilization"], 0.0)
        self.assertEqual(results["volunteer_utilization"], 0.0)

    def test_duplicate_assignments(self):
        """The same donation should never be counted twice."""

        donations = {
            "D1": donation("D1", 10),
            "D2": donation("D2", 20),
        }

        # D1 accidentally appears twice in the results.
        assignments = [assigned("D1"), assigned("D1")]

        results = calculate_metrics(donations, assignments, {}, {})

        # D1 should count only once.
        self.assertEqual(results["assigned"], 1)
        self.assertEqual(results["rescued_food"], 10)
        self.assertEqual(results["assignment_rate"], 50.0)

    def test_food_at_risk_is_unassigned_quantity(self):
        """Food at risk is the total quantity of donations left unassigned."""

        donations = {
            "D1": donation("D1", 10),
            "D2": donation("D2", 20),
            "D3": donation("D3", 30),
        }
        assignments = [assigned("D1"), unassigned("D2"), unassigned("D3")]

        results = calculate_metrics(donations, assignments, {}, {})

        self.assertEqual(results["food_at_risk"], 50)
        # Rescued plus at risk always adds up to everything that was donated.
        self.assertEqual(
            results["rescued_food"] + results["food_at_risk"],
            results["total_food"],
        )

    def test_urgent_rescue_rate(self):
        """Urgent donations are the earliest-expiring 25% by expiry_time."""

        # Eight donations, so the urgent group is the 2 earliest expiries:
        # D3 (minute 20) and D5 (minute 30). Arrival order is not the same as
        # expiry order on purpose.
        expiries = {"D1": 90, "D2": 80, "D3": 20, "D4": 70,
                    "D5": 30, "D6": 60, "D7": 50, "D8": 40}
        donations = {
            donation_id: donation(donation_id, 10, expiry, order)
            for order, (donation_id, expiry) in enumerate(expiries.items())
        }

        # D3 is rescued but D5 is not, so half of the urgent group is rescued.
        assignments = [assigned("D3"), unassigned("D5"), assigned("D1")]

        results = calculate_metrics(donations, assignments, {}, {})

        self.assertEqual(results["urgent_donations"], 2)
        self.assertEqual(results["urgent_assigned"], 1)
        self.assertEqual(results["urgent_rescue_rate"], 50.0)

    def test_urgent_group_rounds_up_to_at_least_one(self):
        """With fewer than 4 donations, the urgent group is still 1 donation."""

        donations = {
            "D1": donation("D1", 10, expiry_time=50, arrival_order=0),
            "D2": donation("D2", 10, expiry_time=40, arrival_order=1),
        }

        results = calculate_metrics(donations, [assigned("D2")], {}, {})

        self.assertEqual(results["urgent_donations"], 1)
        self.assertEqual(results["urgent_rescue_rate"], 100.0)

    def test_urgent_ties_go_to_earlier_arrival(self):
        """Donations with the same expiry are ranked by arrival order."""

        donations = {
            "D1": donation("D1", 10, expiry_time=40, arrival_order=0),
            "D2": donation("D2", 10, expiry_time=40, arrival_order=1),
            "D3": donation("D3", 10, expiry_time=90, arrival_order=2),
            "D4": donation("D4", 10, expiry_time=90, arrival_order=3),
        }

        # D1 and D2 tie on expiry; D1 arrived first, so D1 is the urgent one.
        results = calculate_metrics(donations, [assigned("D2")], {}, {})
        self.assertEqual(results["urgent_rescue_rate"], 0.0)

        results = calculate_metrics(donations, [assigned("D1")], {}, {})
        self.assertEqual(results["urgent_rescue_rate"], 100.0)

    def test_recipient_utilization_uses_all_recipients(self):
        """Utilization divides by the capacity of every recipient."""

        donations = {"D1": donation("D1", 30)}
        # 30 assigned units out of 40 + 60 total recipient capacity.
        recipients = {"R1": recipient(40), "R2": recipient(60)}

        results = calculate_metrics(
            donations, [assigned("D1")], recipients, {}
        )

        self.assertEqual(results["recipient_utilization"], 30.0)

    def test_volunteer_utilization_counts_every_pickup_slot(self):
        """Utilization divides by vehicle capacity times maximum pickups."""

        donations = {"D1": donation("D1", 30)}
        # V1 can carry 20 x 2 = 40 and V2 can carry 10 x 2 = 20, so 60 total.
        volunteers = {"V1": volunteer(20, 2), "V2": volunteer(10, 2)}

        results = calculate_metrics(
            donations, [assigned("D1")], {}, volunteers
        )

        self.assertEqual(results["volunteer_utilization"], 50.0)


if __name__ == "__main__":
    unittest.main()
