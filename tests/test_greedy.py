import unittest

from rescueroute.models import Status
from tests.helpers import ensure_sample_data, run_greedy_scenario

def setUpModule():
    ensure_sample_data()

class TestGreedy(unittest.TestCase):
    def test_starvation_defers_canned_goods(self):
        result = run_greedy_scenario("starvation")
        self.assertEqual(result["D-1001"].status, Status.UNASSIGNED)
        self.assertIn("D-1005", result["D-1001"].decision_reason)