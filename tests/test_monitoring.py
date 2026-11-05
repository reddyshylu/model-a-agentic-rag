"""Clinician approval (human in the loop). Needs langgraph: pip install -r requirements-core.txt"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a import config  # noqa: E402


@unittest.skipUnless(importlib.util.find_spec("langgraph"), "langgraph not installed")
class TestClinicianQueue(unittest.TestCase):
    def setUp(self):
        self.saved = config.ESCALATIONS
        config.ESCALATIONS = Path(tempfile.mkdtemp())

    def tearDown(self):
        config.ESCALATIONS = self.saved

    def test_every_alert_waits_for_a_clinician(self):
        from model_a.monitoring import ClinicianQueue
        q = ClinicianQueue()
        new = q.run_monitoring()
        self.assertEqual(len(new), 20)          # all expected alerts, none auto-sent
        self.assertEqual(len(q.done), 0)
        self.assertEqual(q.run_monitoring(), [])  # no duplicates on rerun
        first = q.sorted_pending()[0]["alert"]
        self.assertEqual(first["priority"], "urgent")
        res = q.decide(first["key"], "reject", "Dr. Test")
        self.assertIsNone(res["patient_message"])
        audit = (config.ESCALATIONS / "clinician_audit.jsonl").read_text()
        self.assertIn("reject", audit)
        self.assertNotRegex(audit, r"LW-\d{7}")


if __name__ == "__main__":
    unittest.main()
