"""Emergency voice caller: when Model A raises an URGENT escalation, call the care-team line.

Safety design:
- The model never chooses to call or chooses the number. Only an urgent escalation
  (fixed red-flag rules) triggers a call, and the number comes from .env.
- The number must be in VOICE_ALLOWED_NUMBERS and in +E.164 form, or the call is refused.
  For the demo that list holds only your own verified phone. Never 911 or a real hospital.
- VOICE_MODE=dry_run (default) logs the exact call it would make and never dials.
- One call per escalation per attempt; a per-hour cap stops runaway dialing.
- The call carries only: alert id, fictional MRN, reason, time, clinic callback number.
- Recording is off. All data is fictional.
- Unanswered or unacknowledged calls are retried once, then flagged "unacknowledged".
"""
from __future__ import annotations

import json
import re
import threading
import urllib.request
from datetime import datetime, timedelta, timezone

from . import config, escalation

OUTBOUND_URL = "https://api.elevenlabs.io/v1/convai/twilio/outbound-call"
E164 = re.compile(r"^\+[1-9]\d{7,14}$")


class CallRefused(RuntimeError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _log(row: dict) -> None:
    config.ESCALATIONS.mkdir(parents=True, exist_ok=True)
    with open(config.ESCALATIONS / "calls.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": _now().isoformat(timespec="seconds"), **row}) + "\n")


def call_log() -> list[dict]:
    p = config.ESCALATIONS / "calls.jsonl"
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def check_number(number: str) -> str:
    if not E164.match(number or ""):
        raise CallRefused("number is not in +E.164 form")
    if number in ("+1911", "+911"):
        raise CallRefused("emergency numbers are never dialed by Model A")
    if number not in config.VOICE_ALLOWED_NUMBERS:
        raise CallRefused("number is not in VOICE_ALLOWED_NUMBERS")
    return number


def build_payload(esc: dict, patient_ref: str, to_number: str) -> dict:
    """The full request body. Only these minimal fields leave Model A."""
    when = esc["created"].replace("T", " ").replace("+00:00", " UTC")
    return {
        "agent_id": config.ELEVENLABS_AGENT_ID,
        "agent_phone_number_id": config.ELEVENLABS_PHONE_NUMBER_ID,
        "to_number": to_number,
        "call_recording_enabled": False,
        "conversation_initiation_client_data": {"dynamic_variables": {
            "alert_id": esc["id"],
            "patient_ref": patient_ref,
            "alert_reason": esc["reason"],
            "alert_time": when,
            "callback_number": config.CLINIC_CALLBACK_NUMBER,
        }},
    }


class VoiceCaller:
    def __init__(self, mode: str | None = None, patient_ref=lambda pid: pid, sender=None):
        self.mode = mode or config.VOICE_MODE
        self.patient_ref = patient_ref      # maps patient id to the reference read on the call
        self.sender = sender or self._post  # injectable for tests
        self._lock = threading.Lock()

    def _post(self, payload: dict) -> dict:
        req = urllib.request.Request(OUTBOUND_URL, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json",
                                              "xi-api-key": config.ELEVENLABS_API_KEY})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())

    def call(self, esc: dict, attempt: int = 1) -> dict:
        """Place (or dry-run) one call for an urgent escalation. Never raises."""
        with self._lock:
            base = {"escalation_id": esc["id"], "patient_id": esc["patient_id"], "attempt": attempt, "mode": self.mode}
            if self.mode == "off":
                return {**base, "status": "off"}
            log = call_log()
            if any(r["escalation_id"] == esc["id"] and r["attempt"] == attempt and r["status"] in ("dry_run", "placed")
                   for r in log):
                return {**base, "status": "duplicate_skipped"}
            hour_ago = _now() - timedelta(hours=1)
            recent = [r for r in log if r["status"] in ("dry_run", "placed")
                      and datetime.fromisoformat(r["time"]) > hour_ago]
            if len(recent) >= config.VOICE_MAX_CALLS_PER_HOUR:
                row = {**base, "status": "rate_limited"}
                _log(row)
                return row
            try:
                to = check_number(config.VOICE_CARE_TEAM_NUMBER)
            except CallRefused as exc:
                row = {**base, "status": "refused", "reason": str(exc)}
                _log(row)
                return row
            payload = build_payload(esc, self.patient_ref(esc["patient_id"]), to)
            if self.mode == "dry_run":
                row = {**base, "status": "dry_run", "to": to,
                       "variables": payload["conversation_initiation_client_data"]["dynamic_variables"]}
                _log(row)
                return row
            if not (config.ELEVENLABS_API_KEY and config.ELEVENLABS_AGENT_ID and config.ELEVENLABS_PHONE_NUMBER_ID):
                row = {**base, "status": "error", "reason": "ElevenLabs settings missing in .env"}
                _log(row)
                return row
            try:
                res = self.sender(payload)
                row = {**base, "status": "placed" if res.get("success", True) else "error", "to": to,
                       "conversation_id": res.get("conversation_id"), "call_sid": res.get("callSid")}
            except Exception as exc:
                row = {**base, "status": "error", "reason": repr(exc)[:200]}
            _log(row)
            return row


# ---------------------------------------------------------------- after the call
def next_action(event: dict, attempt: int) -> str:
    """Decide what happens after ElevenLabs reports on a call.
    acknowledged | retry | flag_unacknowledged | ignore"""
    kind = event.get("type")
    data = event.get("data", {})
    if kind == "post_call_transcription":
        dc = (data.get("analysis") or {}).get("data_collection_results") or {}
        ack = (dc.get("acknowledged") or {}).get("value")
        if ack is True or str(ack).lower() in ("true", "yes"):
            return "acknowledged"
    elif kind != "call_initiation_failure":
        return "ignore"
    return "retry" if attempt < config.VOICE_MAX_ATTEMPTS else "flag_unacknowledged"


def handle_event(event: dict, caller: VoiceCaller, schedule=None) -> dict:
    """Process a verified post-call webhook event. Returns what was done."""
    conv = (event.get("data") or {}).get("conversation_id")
    match = [r for r in call_log() if r.get("conversation_id") == conv and conv]
    if not match:
        return {"action": "ignore", "reason": "unknown conversation"}
    last = match[-1]
    action = next_action(event, last["attempt"])
    if action == "acknowledged":
        escalation.update_status(last["escalation_id"], "acknowledged_by_phone")
    elif action == "flag_unacknowledged":
        escalation.update_status(last["escalation_id"], "unacknowledged")
    elif action == "retry":
        esc = escalation.get(last["escalation_id"])
        run = schedule or (lambda fn: threading.Timer(config.VOICE_RETRY_SECONDS, fn).start())
        run(lambda: caller.call(esc, last["attempt"] + 1))
    _log({"escalation_id": last["escalation_id"], "patient_id": last["patient_id"], "attempt": last["attempt"],
          "mode": caller.mode, "status": f"outcome:{action}", "conversation_id": conv})
    return {"action": action, "escalation_id": last["escalation_id"]}


_registered = False


def register(store=None) -> VoiceCaller | None:
    """Hook the caller into urgent escalations (once per process)."""
    global _registered
    if config.VOICE_MODE == "off" or _registered:
        return None
    ref = (lambda pid: store.patients[pid]["mrn"]) if store else (lambda pid: pid)
    caller = VoiceCaller(patient_ref=ref)
    escalation.on_urgent(caller.call)
    _registered = True
    return caller
