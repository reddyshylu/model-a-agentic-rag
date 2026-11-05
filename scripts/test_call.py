"""Demo: raise one urgent escalation for a fictional patient and run the voice caller.

    python scripts/test_call.py --patient P20
Respects VOICE_MODE: dry_run only logs the call; live dials VOICE_CARE_TEAM_NUMBER
(which must be in VOICE_ALLOWED_NUMBERS). Use only your own verified phone.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a import config, escalation, voice  # noqa: E402
from model_a.records import RecordStore  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--patient", default="P20")
a = ap.parse_args()
voice.register(RecordStore())
esc = escalation.raise_escalation(a.patient, "urgent", "TEST CALL: red-flag symptom in chat: like tar", "test_call")
print(f"VOICE_MODE={config.VOICE_MODE}  escalation {esc['id']}")
print("last call log row:", voice.call_log()[-1])
