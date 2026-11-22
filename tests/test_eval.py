import json
import tempfile
import unittest

from accounting_eval.grader import extract_answer, grade, parse_number
from accounting_eval.runner import grade_responses, load_tasks, oracle_model, run, summarize


class TestParsing(unittest.TestCase):
    def test_extract_last_answer(self):
        self.assertEqual(extract_answer("ANSWER: 1\nwait\nANSWER: $2,000"), "$2,000")
        self.assertIsNone(extract_answer("the answer is 5"))

    def test_parse_number(self):
        self.assertEqual(parse_number("$1,234.50"), 1234.5)
        self.assertEqual(parse_number("(500)"), -500)
        self.assertEqual(parse_number("35%"), 35)
        self.assertEqual(parse_number("-12"), -12)
        self.assertIsNone(parse_number("none"))


class TestGrading(unittest.TestCase):
    num = {"id": "x", "category": "c", "type": "numeric", "answer": 9000, "tolerance": 0.5}
    mc = {"id": "y", "category": "c", "type": "choice", "answer": "B"}

    def test_numeric(self):
        self.assertTrue(grade(self.num, "work...\nANSWER: $9,000")["correct"])
        self.assertFalse(grade(self.num, "ANSWER: 9001")["correct"])
        self.assertFalse(grade(self.num, "9000")["correct"])

    def test_choice(self):
        self.assertTrue(grade(self.mc, "ANSWER: B")["correct"])
        self.assertTrue(grade(self.mc, "ANSWER: **b)**")["correct"])
        self.assertFalse(grade(self.mc, "ANSWER: A")["correct"])


class TestDataset(unittest.TestCase):
    def test_tasks_well_formed(self):
        tasks = load_tasks()
        self.assertGreaterEqual(len(tasks), 20)
        self.assertEqual(len({t["id"] for t in tasks}), len(tasks))
        for t in tasks:
            self.assertIn(t["type"], {"numeric", "choice"})
            for key in ("id", "category", "prompt", "answer"):
                self.assertIn(key, t)

    def test_oracle_scores_100(self):
        s = summarize(run(load_tasks(), oracle_model))
        self.assertEqual(s["accuracy"], 1.0)

    def test_grade_responses_file(self):
        tasks = load_tasks(category="ratios")
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write(json.dumps({"id": "rat-001", "response": "ANSWER: 2"}) + "\n")
        s = summarize(grade_responses(tasks, f.name))
        self.assertEqual(s["correct"], 1)
        self.assertEqual(s["total"], len(tasks))


if __name__ == "__main__":
    unittest.main()
