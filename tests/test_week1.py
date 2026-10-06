"""
Week 1 tests: five required cases, run against the FIFO baseline and the loader.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by AidanDao, see docs/TOOLS_AND_SOURCES.md

Run from the repo root:  python -m unittest discover -s tests -t .

Each test loads a hand-built dataset from data/scenarios/ (see data/README.md).
Assertions on explanation text only check for a key word (e.g. "capacity"), so
the wording of the messages stays up to whoever writes them.
"""

import unittest

from rescueroute.models import Status
from tests.helpers import ensure_sample_data, load_scenario, run_fifo_scenario


def setUpModule():
    ensure_sample_data()


class TestWeek1(unittest.TestCase):

    def test_normal_match(self):
        """A compatible donor, recipient, and volunteer produce an assignment."""
        result = run_fifo_scenario("normal_match")

        a = result["D-1001"]
        self.assertEqual(a.status, Status.ASSIGNED)
        self.assertEqual(a.recipient_id, "R-201")
        self.assertEqual(a.volunteer_id, "V-301")
        self.assertIn("D-1001", a.decision_reason)

    def test_duplicate_ids_are_flagged(self):
        """A repeated donation, recipient, or volunteer ID is reported by validation."""
        donations, recipients, volunteers, errors = load_scenario("duplicate_ids")

        for kind, dup_id in [("donations", "D-1001"), ("recipients", "R-201"), ("volunteers", "V-301")]:
            with self.subTest(kind=kind):
                self.assertTrue(any(dup_id in e for e in errors[kind]),
                                f"no {kind} error mentions {dup_id}: {errors[kind]}")
        # The first record wins; the duplicate must not silently replace or add to it.
        self.assertEqual(len(donations), 2)     # D-1001, D-1002
        self.assertEqual(donations["D-1001"].donor_name, "Campus Dining Hall")
        self.assertEqual(len(recipients), 1)
        self.assertEqual(len(volunteers), 1)

    def test_expired_donation_is_not_assigned(self):
        """A donation that expires at its ready time cannot be rescued; others still are."""
        result = run_fifo_scenario("expired_donation")

        expired = result["D-1001"]       # expiry_time == ready_time
        self.assertEqual(expired.status, Status.UNASSIGNED)
        self.assertIsNone(expired.recipient_id)
        self.assertIn("expir", expired.decision_reason.lower())

        self.assertEqual(result["D-1003"].status, Status.ASSIGNED)
        # D-1002 (10 minutes left) is deliberately not asserted: whether that is
        # enough time depends on the team's pickup-time rule. It still needs an explanation.
        self.assertTrue(result["D-1002"].decision_reason)

    def test_no_compatible_food_type(self):
        """No recipient accepts dairy, so the donation is unassigned with an explanation."""
        result = run_fifo_scenario("no_compatible_food_type")

        a = result["D-1001"]
        self.assertEqual(a.status, Status.UNASSIGNED)
        self.assertIsNone(a.recipient_id)
        self.assertIsNone(a.volunteer_id)
        reason = a.decision_reason.lower()
        self.assertTrue("dairy" in reason or "food type" in reason, reason)

    def test_insufficient_recipient_capacity(self):
        """150 units fit no recipient (largest holds 100), so the donation is unassigned."""
        result = run_fifo_scenario("insufficient_recipient_capacity")

        a = result["D-1001"]
        self.assertEqual(a.status, Status.UNASSIGNED)
        self.assertIsNone(a.recipient_id)
        self.assertIn("capacity", a.decision_reason.lower())


if __name__ == "__main__":
    unittest.main()
