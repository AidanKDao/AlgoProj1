"""
Tests for the busy-volunteer schedule (rule 002, "Volunteer schedule"): a volunteer cannot
take overlapping trips, free time before a booked trip can be used, and cross-area trips
take longer.

AI-assisted: Claude Code (claude-sonnet-5-5), requested by Kaleb Robles, see docs/TOOLS_AND_SOURCES.md

Each test loads a hand-built scenario from data/scenarios/ (made by data/scripts/generate_data.py).
"""

import unittest

from rescueroute.feasibility import CapacityTracker, Rules, schedule
from rescueroute.models import Donation, Recipient, Status, Volunteer
from tests.helpers import ensure_sample_data, run_fifo_scenario, run_greedy_scenario


def setUpModule():
    ensure_sample_data()


# make: one donation, recipient and volunteer, all in the central area, plus a fresh tracker.
def make(ready=0):
    donation = Donation("D-1", "Donor", "produce", 10, ready, 1000, "central", 0)
    recipient = Recipient("R-1", "Shelter", {"produce"}, 100, 720, "central")
    volunteer = Volunteer("V-1", 40, 4, 0, 720, "central")
    return donation, recipient, volunteer, CapacityTracker({"R-1": recipient}, {"V-1": volunteer})


class TestBusyVolunteer(unittest.TestCase):

    # FIFO books V-301 for D-1001 first (0 to 15). D-1002 would then start at 15 and arrive
    # too late (it expires at 40), so it is unassigned and the explanation says the volunteer is busy.
    def test_fifo_leaves_urgent_donation_unassigned_because_volunteer_is_busy(self):
        result = run_fifo_scenario("volunteer_busy")
        self.assertEqual(result["D-1001"].status, Status.ASSIGNED)
        self.assertEqual(result["D-1002"].status, Status.UNASSIGNED)
        self.assertIn("busy", result["D-1002"].decision_reason)

    # Greedy processes the sooner-expiring D-1002 first, so both donations fit one after the other.
    def test_greedy_assigns_both_one_after_the_other(self):
        result = run_greedy_scenario("volunteer_busy")
        self.assertEqual((result["D-1002"].scheduled_time_start, result["D-1002"].scheduled_time_end), (0, 15))
        self.assertEqual((result["D-1001"].scheduled_time_start, result["D-1001"].scheduled_time_end), (15, 30))

    # No volunteer is ever booked for overlapping trips, in any strategy, on any scenario.
    def test_no_overlapping_trips_for_any_volunteer(self):
        for scenario in ("volunteer_busy", "volunteer_gap_filling", "starvation", "competing_capacity"):
            for run in (run_fifo_scenario, run_greedy_scenario):
                with self.subTest(scenario=scenario, strategy=run.__name__):
                    trips = {}
                    for a in run(scenario).values():
                        if a.status == Status.ASSIGNED:
                            trips.setdefault(a.volunteer_id, []).append(
                                (a.scheduled_time_start, a.scheduled_time_end))
                    for booked in trips.values():
                        booked.sort()
                        for (_, end), (next_start, _) in zip(booked, booked[1:]):
                            self.assertLessEqual(end, next_start)


class TestGapFilling(unittest.TestCase):

    # Greedy places D-1001 (300 to 315) first. D-1002 (ready 0) then uses the free time before
    # it, and D-1003 (ready 305) overlaps the booked trip so it is pushed to start at 315.
    def test_free_time_is_used_and_overlap_is_pushed_back(self):
        result = run_greedy_scenario("volunteer_gap_filling")
        self.assertEqual(result["D-1001"].scheduled_time_start, 300)
        self.assertEqual(result["D-1002"].scheduled_time_start, 0)
        self.assertEqual(result["D-1003"].scheduled_time_start, 315)
        self.assertEqual(result["D-1003"].scheduled_time_end, 330)

    # schedule() directly: a trip booked from 0 to 15 moves a new trip to start at 15 (half-open
    # intervals: a trip ending at 15 lets the next start at 15), and without a tracker it is free.
    def test_schedule_moves_start_to_end_of_booked_trip(self):
        d, r, v, t = make(ready=0)
        t.record(d, "R-1", "V-1", 0, 15)
        self.assertEqual(schedule(d, v, r, Rules(), t), (15, 30))
        self.assertEqual(schedule(d, v, r, Rules()), (0, 15))

    # A new trip that fits entirely before a booked trip is not moved.
    def test_schedule_uses_gap_before_booked_trip(self):
        d, r, v, t = make(ready=0)
        t.record(d, "R-1", "V-1", 300, 315)
        self.assertEqual(schedule(d, v, r, Rules(), t), (0, 15))

    # Booked trips are not changed by loading or by reading: a fresh tracker has no trips.
    def test_fresh_tracker_has_no_booked_trips(self):
        _, _, _, t = make()
        self.assertEqual(t.volunteer_trips, {"V-1": []})


class TestCrossAreaTrips(unittest.TestCase):

    # Volunteers live in the north, donations are in the south, the recipient is in the east,
    # so a trip takes 15 + 15 + 15 = 45 minutes. D-1001 (expires 60) just fits (45 + 15);
    # D-1002 (expires 59) does not.
    def test_cross_area_trip_takes_45_minutes(self):
        for run in (run_fifo_scenario, run_greedy_scenario):
            with self.subTest(strategy=run.__name__):
                result = run("cross_area_trip")
                self.assertEqual(result["D-1001"].status, Status.ASSIGNED)
                self.assertEqual(result["D-1001"].scheduled_time_end, 45)
                self.assertEqual(result["D-1002"].status, Status.UNASSIGNED)
                self.assertIn("expires at minute 59", result["D-1002"].decision_reason)


if __name__ == "__main__":
    unittest.main()
