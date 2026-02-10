import core
from core import schedule_next_review, build_study_plan
import unittest


class TestSpacedRepetition(unittest.TestCase):
    def setUp(self):
        core.vocab.clear()
    # Testing schedule_next_review
    def test_next_review(self):
        core.vocab["test"] = {
            "ease": 2.5 ,
            "interval": 5,
            "box": 2
        }
        schedule_next_review("test", rating = 1)
        self.assertEqual(core.vocab["test"]["interval"], 1)
    def test_next_review_easy(self):
        core.vocab["test"] = {
            "ease": 2.5,
            "interval": 5,
            "box": 2
        }
        schedule_next_review("test", rating = 4)
        self.assertGreater(core.vocab["test"]["interval"], 5)
    def test_lowering_interval(self):
        core.vocab["test"] = {
            "ease": 2.5,
            "interval": 1,
            "box": 2
        }
        schedule_next_review("test", rating = 4)
        self.assertEqual(core.vocab["test"]["interval"], 3)
    def test_low_ease_prioritized(self):
        core.vocab["test"] = {
            "ease": 2.5,
            "interval": 5,
            "box": 2
        }
        schedule_next_review("test", rating = 1)
        self.assertGreater(core.vocab["test"]["ease"], 1.3)

#testing build_study_plan()
    def test_overdue(self):
        core.vocab["past"] = {
            "next_review": "2000-09-01",
            "ease": 2.5,
            "times_reviewed": 5,
            "times_correct": 5,
            "history": []
        }

        core.vocab["future"] = {
            "next_review": "2099-09-01",
            "ease": 2.5,
            "times_reviewed": 5,
            "times_correct": 5,
            "history": []
        }

        plan = core.build_study_plan(1)
        self.assertEqual(plan[0], "past")

    def test_new_words(self):
        core.vocab["new"] = {
            "next_review": "2099-09-01",
            "ease": 2.5,
            "times_reviewed": 0,
            "history": []
        }
        plan = core.build_study_plan(1)
        self.assertEqual(plan[0], "new")
    def test_low_accuracy_prioritized(self):
        core.vocab["hard"] = {
            "times_reviewed": 10,
            "times_correct": 2,
            "next_review": "2099-01-01",
            "ease": 2.5,
            "history": []
        }

        core.vocab["easy"] = {
            "times_reviewed": 10,
            "times_correct": 10,
            "next_review": "2099-01-01",
            "ease": 2.5,
            "history": []
        }

        plan = core.build_study_plan(1)

        self.assertEqual(plan[0], "hard")
if __name__ == "__main__":
    unittest.main()