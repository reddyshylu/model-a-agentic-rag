"""Listen-layer tests: the spoken version only shortens, never adds."""
import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from model_a import config, speech  # noqa: E402
from model_a.pipeline import ModelA  # noqa: E402


class TestSpeech(unittest.TestCase):
    def test_every_golden_answer_has_a_safe_spoken_version(self):
        m = ModelA()
        rows = list(csv.DictReader(open(config.GOLDEN, encoding="utf-8")))
        for r in rows:
            a = m.ask(m.start_session(r["patient_id"]), r["question"])
            sp = speech.spoken_version(a.text, a.route)
            self.assertEqual(speech.check_spoken(sp, a.text), [], r["id"])
            self.assertNotRegex(sp, r"\[[^\]]+\]", r["id"])  # no citation tags read aloud
            if a.route != "answer":
                self.assertEqual(sp, a.text, r["id"])  # fixed messages word for word
            else:
                self.assertLessEqual(sp.count(". "), speech.config.SPOKEN_MAX_POINTS + 2, r["id"])

    def test_added_numbers_are_caught(self):
        self.assertTrue(speech.check_spoken("Your ALT is 52.", "Your ALT was 66.0 U/L on 2026-05-20."))
        self.assertFalse(speech.check_spoken("Your ALT was 66 on May 20, 2026.", "Your ALT was 66.0 U/L on 2026-05-20."))

    def test_speech_friendly_text(self):
        t = speech.for_speech("ALT 66.0 U/L on 2026-05-20 [labs ALT]")
        self.assertEqual(t, "ALT 66 units per liter on May 20, 2026")

    def test_no_audio_without_settings(self):
        saved = config.ELEVENLABS_VOICE_ID
        config.ELEVENLABS_VOICE_ID = ""
        try:
            self.assertIsNone(speech.text_to_speech("hello"))
        finally:
            config.ELEVENLABS_VOICE_ID = saved


if __name__ == "__main__":
    unittest.main()
