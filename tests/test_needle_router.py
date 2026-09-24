"""
Fast regression tests for the Needle command router's rule layer (no model inference).

Checks every evaluation request routes to the right place by triggers/gates alone, plus the
argument readers (age, device, scan type, topic). Needs the cactus-needle package (for @tool).
The full model-in-the-loop evaluation is scripts/needle_router_eval.py.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))

try:
    from guardian_interpreter import needle_router as R
    import needle_router_eval as ev
except ImportError as e:  # cactus-needle not installed
    raise unittest.SkipTest(f"needle not available: {e}")

ALL_CASES = ev.DEV + ev.HELDOUT + ev.FRESH + ev.FRESH2


class TestTriggerPatterns(unittest.TestCase):
    def test_no_mangled_word_boundaries(self):
        # A "\b" that became a backspace char or a literal "b" silently disables a trigger.
        for name, pats in R.TRIGGERS.items():
            for p in pats:
                self.assertNotIn("\x08", p.pattern, name)
                self.assertFalse(p.pattern.startswith("b("), f"{name}: {p.pattern[:40]}")


class TestRoutingDecision(unittest.TestCase):
    def test_commands_reach_their_tools(self):
        for query, expected in ALL_CASES:
            if not expected:
                continue
            with self.subTest(query=query):
                explain = R.EXPLAIN_RE.search(query) and not R.OWN_KIT_CHECK_RE.search(query)
                self.assertFalse(explain, "command gated as an explanation")
                cands = {c for clause in R.split_clauses(query) for c in R.candidates(clause)}
                for name, _ in expected:
                    self.assertIn(name, cands)

    def test_questions_go_to_llm(self):
        for query, expected in ALL_CASES:
            if expected:
                continue
            with self.subTest(query=query):
                explain = R.EXPLAIN_RE.search(query) and not R.OWN_KIT_CHECK_RE.search(query)
                cands = [c for clause in R.split_clauses(query) for c in R.candidates(clause)]
                self.assertTrue(explain or not cands, f"would call {cands}")

    def test_compound_commands_split(self):
        self.assertEqual(R.split_clauses("turn off the kettle and the living room lights"),
                         ["turn off the kettle", "turn off the living room lights"])
        self.assertEqual(len(R.split_clauses("start a lesson about scams and phishing for my son")), 1)


class TestArgumentReaders(unittest.TestCase):
    def test_age_group(self):
        cases = {"my 8 year old": "child", "my daughter is 15": "teen", "my twelve year old": "child",
                 "my 13-year-old": "teen", "a year 9 student": "teen", "my year 3 son": "child",
                 "my teenage son": "teen", "my little boy": "child", "the kids": None}
        for text, group in cases.items():
            self.assertEqual(R.detect_age_group(text), group, text)

    def test_scan_type(self):
        self.assertEqual(R.fix_args("scan_network", "check for open ports", {})["scan_type"], "port")
        self.assertEqual(R.fix_args("scan_network", "scan everything, ports too", {})["scan_type"], "full")
        self.assertEqual(R.fix_args("scan_network", "quick scan", {"scan_type": "full"})["scan_type"], "ping")

    def test_device(self):
        self.assertEqual(R.detect_device("switch the lounge lights off"), "lights_living")
        self.assertEqual(R.detect_device("is the boiler on"), "hot_water")
        self.assertIsNone(R.detect_device("turn off the kettle and the bedroom lights"))  # ambiguous

    def test_topic(self):
        self.assertEqual(R.detect_topic("teach my 8 year old about strong passwords"), "strong passwords")
        self.assertEqual(R.detect_topic("a password game for the little ones"), "password")
        self.assertEqual(R.detect_topic("teach my 10 year old how to spot fake websites"), "spot fake websites")


if __name__ == "__main__":
    unittest.main()
