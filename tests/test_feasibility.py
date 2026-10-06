"""
Feasibility and capacity-tracking tests, including the not-yet-settled rules when switched on.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

How these tests work: each test method (named test_...) builds a small situation, calls the
feasibility code, then uses assert methods to check the result.
    assertIsNone(x)     passes if x is None (for check_pair, None means the match is feasible)
    assertIsNotNone(x)  passes if x is anything but None
    assertIn(a, b)      passes if a is inside b (here, a keyword inside a failure message)
    assertEqual(a, b)   passes if a == b
"""

import unittest

from rescueroute.feasibility import (CapacityTracker, Rules, check_pair, find_match,
                                     unassigned_reason)
from rescueroute.models import Donation, Recipient, Volunteer
from tests.helpers import ensure_sample_data, load_scenario


# setUpModule: unittest runs this once before any test in the file. It makes sure the sample
# data in data/scenarios/ exists, because that folder is not stored in git.
def setUpModule():
    ensure_sample_data()


# make: a helper (not a test) that builds one valid donation, recipient, volunteer, and a
# fresh tracker. Each test calls it and changes just one thing through the keyword arguments
# (quantity=50, food="frozen", ...), so it is clear which change caused the result.
# The fixed values: recipient holds 100 and accepts dairy/produce until minute 600; the
# volunteer's vehicle holds 60, with 2 pickups, available from minute 0 to 480.
def make(quantity=30, ready=0, expiry=120, food="dairy", area="central"):
    donation = Donation("D-1", "Donor", food, quantity, ready, expiry, area, 0)
    recipient = Recipient("R-1", "Shelter", {"dairy", "produce"}, 100, 600, "central")
    volunteer = Volunteer("V-1", 60, 2, 0, 480, "central")
    tracker = CapacityTracker({"R-1": recipient}, {"V-1": volunteer})
    return donation, recipient, volunteer, tracker


# These tests cover the rules that are always on. In each test, d, r, v, t stand for the
# donation, recipient, volunteer, and tracker returned by make().
class TestSettledChecks(unittest.TestCase):

    # Everything is compatible, so check_pair returns None (no problem found).
    def test_compatible_triple_is_feasible(self):
        d, r, v, t = make()
        self.assertIsNone(check_pair(d, r, v, t, Rules()))

    # The recipient only accepts dairy and produce, so frozen food is rejected and the
    # message names the food type.
    def test_wrong_food_type_rejected(self):
        d, r, v, t = make(food="frozen")
        self.assertIn("frozen", check_pair(d, r, v, t, Rules()))

    # Capacity is shared across donations: after a 50-unit donation is recorded, only 50 of
    # the recipient's 100 units remain, so a second donation of 60 must be rejected.
    def test_quantity_over_remaining_capacity_rejected(self):
        d, r, v, t = make(quantity=50)
        t.record(d, "R-1", "V-1")                  # 50 used, 50 left
        d2 = Donation("D-2", "Donor", "dairy", 60, 0, 120, "central", 1)
        self.assertIn("capacity", check_pair(d2, r, v, t, Rules()))

    # The volunteer's vehicle holds 60, so a 61-unit donation is rejected.
    def test_vehicle_too_small_rejected(self):
        d, r, v, t = make(quantity=61)
        self.assertIn("vehicle", check_pair(d, r, v, t, Rules()))

    # A donation whose expiry equals its ready time was already expired when it became
    # available, so it is rejected.
    def test_expiry_equal_to_ready_is_expired(self):
        d, r, v, t = make(ready=60, expiry=60)
        self.assertIn("expired", check_pair(d, r, v, t, Rules()))

    # With a 30-minute trip, a pickup at minute 590 arrives at 620, after the recipient
    # closes at 600, so it is rejected.
    def test_recipient_closed_on_arrival_rejected(self):
        d, r, v, t = make(ready=590, expiry=900)
        self.assertIn("closes", check_pair(d, r, v, t, Rules(travel_minutes=30)))

    # Recording an assignment must change only the tracker. The Recipient object keeps its
    # original capacity of 100, and a brand new tracker starts again from the full 100.
    def test_inputs_are_not_mutated_by_tracking(self):
        d, r, v, t = make()
        t.record(d, "R-1", "V-1")
        self.assertEqual(r.capacity, 100)
        self.assertEqual(CapacityTracker({"R-1": r}, {"V-1": v}).recipient_remaining["R-1"], 100)


class TestOptionalRules(unittest.TestCase):
    """Each switch does what its name says. Area match and travel time are still unsettled (off by default)."""

    # Proposal 001 (travel 30, buffer 15): D-1002 expires at minute 10, so it can't arrive in
    # time. Checks that find_match finds nothing for it, the explanation says why, and the
    # other donation (D-1003) is still matched.
    def test_proposal_001_values_reject_ten_minutes_left(self):
        donations, recipients, volunteers, _ = load_scenario("expired_donation")
        rules = Rules(travel_minutes=30, min_minutes_left=15)
        tracker = CapacityTracker(recipients, volunteers)
        self.assertIsNone(find_match(donations["D-1002"], recipients, volunteers, tracker, rules))
        self.assertIn("expires at minute 10",
                      unassigned_reason(donations["D-1002"], recipients, volunteers, tracker, rules))
        self.assertIsNotNone(find_match(donations["D-1003"], recipients, volunteers, tracker, rules))

    # The donation is in the north but the recipient and volunteer are central. The default
    # rules ignore area, so it passes; with require_area_match on, it is rejected.
    def test_area_match(self):
        d, r, v, t = make(area="north")
        self.assertIsNone(check_pair(d, r, v, t, Rules()))
        self.assertIn("areas", check_pair(d, r, v, t, Rules(require_area_match=True)))

    # The volunteer's maximum is 2 pickups. After recording two, the default rules reject a
    # third; switching the rule off lets it through.
    def test_maximum_pickups(self):
        d, r, v, t = make(quantity=5)
        t.record(d, "R-1", "V-1")
        t.record(d, "R-1", "V-1")                  # volunteer's maximum is 2
        self.assertIn("maximum", check_pair(d, r, v, t, Rules()))      # enforced by default
        self.assertIsNone(check_pair(d, r, v, t, Rules(enforce_maximum_pickups=False)))

    # The volunteer is only available until minute 480. A pickup at 470 with a 30-minute trip
    # arrives at 500, so it is rejected by default and accepted when the rule is off.
    def test_volunteer_window(self):
        d, r, v, t = make(ready=470, expiry=900)
        rules = Rules(travel_minutes=30)                                # window enforced by default
        self.assertIn("available", check_pair(d, r, v, t, rules))
        self.assertIsNone(check_pair(d, r, v, t, Rules(travel_minutes=30, enforce_volunteer_window=False)))


# These tests cover the human-readable explanation text for donations that were not assigned.
class TestExplanations(unittest.TestCase):

    # For three scenarios (food type, capacity, vehicle), the explanation must name the
    # donation ID and mention the real cause. `word` is the keyword each message must contain.
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

    # With no recipients and no volunteers at all, there must still be an explanation
    # instead of a crash. `{}` is an empty dict.
    def test_empty_inputs_have_an_explanation(self):
        d, _, _, _ = make()
        text = unassigned_reason(d, {}, {}, CapacityTracker({}, {}), Rules())
        self.assertIn("no recipients", text)


# Lets you run this one file directly with: python3 tests/test_feasibility.py
if __name__ == "__main__":
    unittest.main()
