"""
Feasibility and capacity-tracking tests, including the not-yet-settled rules when switched on.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md
"""

import unittest

from rescueroute.feasibility import (CapacityTracker, Rules, check_pair, find_match,
                                     unassigned_reason)
from rescueroute.models import Donation, Recipient, Volunteer
from tests.helpers import ensure_sample_data, load_scenario


def setUpModule():
    ensure_sample_data()


def make(quantity=30, ready=0, expiry=120, food="dairy", area="central"):
    donation = Donation("D-1", "Donor", food, quantity, ready, expiry, area, 0)
    recipient = Recipient("R-1", "Shelter", {"dairy", "produce"}, 100, 600, "central")
    volunteer = Volunteer("V-1", 60, 2, 0, 480, "central")
    tracker = CapacityTracker({"R-1": recipient}, {"V-1": volunteer})
    return donation, recipient, volunteer, tracker


class TestSettledChecks(unittest.TestCase):

    def test_compatible_triple_is_feasible(self):
        d, r, v, t = make()
        self.assertIsNone(check_pair(d, r, v, t, Rules()))

    def test_wrong_food_type_rejected(self):
        d, r, v, t = make(food="frozen")
        self.assertIn("frozen", check_pair(d, r, v, t, Rules()))

    def test_quantity_over_remaining_capacity_rejected(self):
        d, r, v, t = make(quantity=50)
        t.record(d, "R-1", "V-1")                  # 50 used, 50 left
        d2 = Donation("D-2", "Donor", "dairy", 60, 0, 120, "central", 1)
        self.assertIn("capacity", check_pair(d2, r, v, t, Rules()))

    def test_vehicle_too_small_rejected(self):
        d, r, v, t = make(quantity=61)
        self.assertIn("vehicle", check_pair(d, r, v, t, Rules()))

    def test_expiry_equal_to_ready_is_expired(self):
        d, r, v, t = make(ready=60, expiry=60)
        self.assertIn("expired", check_pair(d, r, v, t, Rules()))

    def test_recipient_closed_on_arrival_rejected(self):
        d, r, v, t = make(ready=590, expiry=900)
        self.assertIn("closes", check_pair(d, r, v, t, Rules(travel_minutes=30)))

    def test_inputs_are_not_mutated_by_tracking(self):
        d, r, v, t = make()
        t.record(d, "R-1", "V-1")
        self.assertEqual(r.capacity, 100)
        self.assertEqual(CapacityTracker({"R-1": r}, {"V-1": v}).recipient_remaining["R-1"], 100)


class TestOptionalRules(unittest.TestCase):
    """Each switch does what its name says. Area match and travel time are still unsettled (off by default)."""

    def test_proposal_001_values_reject_ten_minutes_left(self):
        donations, recipients, volunteers, _ = load_scenario("expired_donation")
        rules = Rules(travel_minutes=30, min_minutes_left=15)
        tracker = CapacityTracker(recipients, volunteers)
        self.assertIsNone(find_match(donations["D-1002"], recipients, volunteers, tracker, rules))
        self.assertIn("expires at minute 10",
                      unassigned_reason(donations["D-1002"], recipients, volunteers, tracker, rules))
        self.assertIsNotNone(find_match(donations["D-1003"], recipients, volunteers, tracker, rules))

    def test_area_match(self):
        d, r, v, t = make(area="north")
        self.assertIsNone(check_pair(d, r, v, t, Rules()))
        self.assertIn("areas", check_pair(d, r, v, t, Rules(require_area_match=True)))

    def test_maximum_pickups(self):
        d, r, v, t = make(quantity=5)
        t.record(d, "R-1", "V-1")
        t.record(d, "R-1", "V-1")                  # volunteer's maximum is 2
        self.assertIn("maximum", check_pair(d, r, v, t, Rules()))      # enforced by default
        self.assertIsNone(check_pair(d, r, v, t, Rules(enforce_maximum_pickups=False)))

    def test_volunteer_window(self):
        d, r, v, t = make(ready=470, expiry=900)
        rules = Rules(travel_minutes=30)                                # window enforced by default
        self.assertIn("available", check_pair(d, r, v, t, rules))
        self.assertIsNone(check_pair(d, r, v, t, Rules(travel_minutes=30, enforce_volunteer_window=False)))


class TestExplanations(unittest.TestCase):

    def test_each_scenario_failure_is_named(self):
        for scenario, word in [("no_compatible_food_type", "accepts"),
                               ("insufficient_recipient_capacity", "capacity"),
                               ("no_volunteer_capacity", "vehicle")]:
            with self.subTest(scenario):
                donations, recipients, volunteers, _ = load_scenario(scenario)
                tracker = CapacityTracker(recipients, volunteers)
                text = unassigned_reason(donations["D-1001"], recipients, volunteers, tracker, Rules())
                self.assertIn("D-1001", text)
                self.assertIn(word, text)

    def test_empty_inputs_have_an_explanation(self):
        d, _, _, _ = make()
        text = unassigned_reason(d, {}, {}, CapacityTracker({}, {}), Rules())
        self.assertIn("no recipients", text)


if __name__ == "__main__":
    unittest.main()
