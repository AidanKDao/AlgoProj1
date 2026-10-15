"""
Week 2 tests: the rest of the required cases from the project brief, run against both
strategies, plus the wording of greedy's deferral sentences.

AI-assisted: Claude Code (claude-opus-5-5), requested by AidanDao, see docs/TOOLS_AND_SOURCES.md

Run from the repo root:  python -m unittest discover -s tests -t .

Scenario tests check statuses, recipients and key words in the explanations, not trip
times, so they keep passing when the busy-volunteer schedule from docs/project_logic/002
is added.
"""

import unittest

from rescueroute.models import Donation, Recipient, Volunteer, Status
from rescueroute.strategies.fifo import run_fifo
from rescueroute.strategies.greedy import run_greedy
from tests.helpers import ensure_sample_data, load_scenario, run_fifo_scenario, run_greedy_scenario


def setUpModule():
    ensure_sample_data()


def assigned_ids(result):
    """The IDs of the assigned donations in a {donation_id: Assignment} result."""
    return {donation_id for donation_id, a in result.items() if a.status == Status.ASSIGNED}


class TestRequiredCases(unittest.TestCase):

    def test_no_volunteer_with_enough_vehicle_capacity(self):
        """90 units fit no vehicle (largest holds 60), so both strategies leave it unassigned."""
        for run in (run_fifo_scenario, run_greedy_scenario):
            with self.subTest(strategy=run.__name__):
                a = run("no_volunteer_capacity")["D-1001"]
                self.assertEqual(a.status, Status.UNASSIGNED)
                self.assertIsNone(a.volunteer_id)
                self.assertIn("vehicle", a.decision_reason.lower())

    def test_two_donations_compete_for_the_same_capacity(self):
        """The recipient holds 50 and both donations are 40 units, so only one fits.
        FIFO takes the one that arrived first (D-1001); greedy takes the one that
        expires first (D-1002)."""
        fifo = run_fifo_scenario("competing_capacity")
        greedy = run_greedy_scenario("competing_capacity")

        self.assertEqual(assigned_ids(fifo), {"D-1001"})
        self.assertEqual(assigned_ids(greedy), {"D-1002"})
        self.assertIn("capacity", fifo["D-1002"].decision_reason.lower())
        self.assertIn("capacity", greedy["D-1001"].decision_reason.lower())

    def test_empty_inputs(self):
        """Header-only files load with no errors, and both strategies return no assignments."""
        donations, recipients, volunteers, errors = load_scenario("empty")

        self.assertEqual(errors, {"donations": [], "recipients": [], "volunteers": []})
        self.assertEqual(run_fifo(donations, recipients, volunteers), [])
        self.assertEqual(run_greedy(donations, recipients, volunteers), [])

    def test_starvation_defers_canned_goods(self):
        """Greedy keeps putting the urgent meals ahead of the canned goods (D-1001) until
        V-301's 4 pickups are used up. The explanation names the closest jumper (D-1005)
        and the greedy level that decided it."""
        greedy = run_greedy_scenario("starvation")

        self.assertEqual(assigned_ids(greedy), {"D-1002", "D-1003", "D-1004", "D-1005"})
        reason = greedy["D-1001"].decision_reason
        self.assertIn("considered after D-1005", reason)
        self.assertIn("expires sooner", reason)

        # FIFO handles the canned goods first, so the last meal is the one left out,
        # and FIFO never reorders, so nothing gets a deferral sentence.
        fifo = run_fifo_scenario("starvation")
        self.assertEqual(assigned_ids(fifo), {"D-1001", "D-1002", "D-1003", "D-1004"})
        self.assertNotIn("considered after", fifo["D-1005"].decision_reason)


# ---------- greedy deferral sentences, on small hand-built inputs ----------

def make_donation(donation_id, food_type, quantity, expiry_time, arrival_order):
    return Donation(donation_id, "Test Donor", food_type, quantity,
                    ready_time=0, expiry_time=expiry_time, pickup_area="central",
                    arrival_order=arrival_order)


def make_recipient(recipient_id, accepted_food_types, capacity):
    return Recipient(recipient_id, f"Recipient {recipient_id}", set(accepted_food_types),
                     capacity, closing_time=720, dropoff_area="central")


def one_pickup_volunteer():
    """A single volunteer with one pickup, so whichever donation greedy handles first
    uses it up and the next one is left unassigned."""
    return {"V-1": Volunteer("V-1", vehicle_capacity=100, maximum_pickups=1,
                             availability_start=0, availability_end=720, pickup_area="central")}


def run_greedy_by_id(donations, recipients, volunteers):
    """Run greedy on lists of records and return {donation_id: Assignment}."""
    result = run_greedy({d.donation_id: d for d in donations},
                        {r.recipient_id: r for r in recipients},
                        volunteers)
    return {a.donation_id: a for a in result}


class TestDeferralSentences(unittest.TestCase):

    def test_tie_on_expiry_decided_by_fewer_compatible_recipients(self):
        """Same expiry: the dairy (1 compatible recipient) goes before the produce (2)."""
        result = run_greedy_by_id(
            [make_donation("D-1", "produce", 10, 200, arrival_order=0),
             make_donation("D-2", "dairy", 10, 200, arrival_order=1)],
            [make_recipient("R-1", ["produce", "dairy"], 10),
             make_recipient("R-2", ["produce"], 10)],
            one_pickup_volunteer())

        self.assertEqual(result["D-2"].status, Status.ASSIGNED)
        self.assertEqual(result["D-1"].status, Status.UNASSIGNED)
        self.assertIn("Donation D-1 was considered after D-2 because both expire at minute 200 "
                      "and D-2 has fewer compatible recipients (1 vs 2).",
                      result["D-1"].decision_reason)

    def test_tie_on_expiry_and_recipients_decided_by_larger_quantity(self):
        """Same expiry and same number of compatible recipients: the larger donation goes first."""
        result = run_greedy_by_id(
            [make_donation("D-1", "produce", 10, 200, arrival_order=0),
             make_donation("D-2", "produce", 20, 200, arrival_order=1)],
            [make_recipient("R-1", ["produce"], 30)],
            one_pickup_volunteer())

        self.assertEqual(result["D-2"].status, Status.ASSIGNED)
        self.assertEqual(result["D-1"].status, Status.UNASSIGNED)
        self.assertIn("Donation D-1 was considered after D-2 because both expire at minute 200 "
                      "with 1 compatible recipient(s) each, and D-2 is larger (20 vs 10 units).",
                      result["D-1"].decision_reason)

    def test_full_tie_keeps_arrival_order_and_adds_no_deferral(self):
        """Tied on levels 1-3: the earlier arrival goes first, so the other one was not jumped."""
        result = run_greedy_by_id(
            [make_donation("D-1", "produce", 10, 200, arrival_order=0),
             make_donation("D-2", "produce", 10, 200, arrival_order=1)],
            [make_recipient("R-1", ["produce"], 30)],
            one_pickup_volunteer())

        self.assertEqual(result["D-1"].status, Status.ASSIGNED)
        self.assertEqual(result["D-2"].status, Status.UNASSIGNED)
        self.assertNotIn("considered after", result["D-2"].decision_reason)

    def test_jumper_with_no_compatible_recipient_is_skipped(self):
        """D-2 (dairy, nobody accepts it) was processed just before D-1, but it could never be
        assigned, so the sentence names D-3, the donation that actually took the pickup."""
        result = run_greedy_by_id(
            [make_donation("D-1", "produce", 10, 200, arrival_order=0),
             make_donation("D-2", "dairy", 10, 150, arrival_order=1),
             make_donation("D-3", "produce", 10, 100, arrival_order=2)],
            [make_recipient("R-1", ["produce"], 30)],
            one_pickup_volunteer())

        self.assertEqual(result["D-3"].status, Status.ASSIGNED)
        reason = result["D-1"].decision_reason
        self.assertIn("considered after D-3 because D-3 expires sooner (minute 100 vs 200).", reason)
        self.assertNotIn("D-2", reason)


if __name__ == "__main__":
    unittest.main()
