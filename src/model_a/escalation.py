"""Escalation queue for the care team, plus hooks for the voice caller (built later).

Urgent alerts go straight out through every registered hook (e.g. the emergency
voice call). High alerts wait in the clinician queue for approval.
Hooks receive only the minimum fields: patient id, tier, reason, time.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Callable

from . import config
from .redact import redact

_urgent_hooks: list[Callable[[dict], None]] = []


def on_urgent(hook: Callable[[dict], None]) -> None:
    """Register a function to call for every urgent escalation (the voice caller plugs in here)."""
    _urgent_hooks.append(hook)


def _write(name: str, row: dict) -> None:
    config.ESCALATIONS.mkdir(parents=True, exist_ok=True)
    with open(config.ESCALATIONS / name, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def raise_escalation(patient_id: str, tier: str, reason: str, source: str) -> dict:
    row = {
        "id": f"esc-{uuid.uuid4().hex[:8]}", "patient_id": patient_id, "tier": tier, "reason": reason,
        "source": source, "status": "open" if tier == "urgent" else "awaiting_clinician",
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    _write("queue.jsonl", row)
    if tier == "urgent":
        minimal = {k: row[k] for k in ("id", "patient_id", "tier", "reason", "created")}
        for hook in _urgent_hooks:
            try:
                hook(minimal)
            except Exception as exc:  # a failed call must never block the patient's urgent message
                _write("hook_errors.jsonl", {"escalation": row["id"], "error": repr(exc)})
    return row


def log_security_event(patient_id: str, kind: str, text: str) -> None:
    _write("security_events.jsonl", {"patient_id": patient_id, "kind": kind, "text": redact(text[:200]),
                                     "time": datetime.now(timezone.utc).isoformat(timespec="seconds")})


def _rows(name: str) -> list[dict]:
    p = config.ESCALATIONS / name
    if not p.exists():
        return []
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def get(escalation_id: str) -> dict | None:
    for r in _rows("queue.jsonl"):
        if r["id"] == escalation_id:
            return r
    return None


def update_status(escalation_id: str, status: str) -> None:
    """Append-only status history; the latest row for an id is its current status."""
    _write("queue_updates.jsonl", {"id": escalation_id, "status": status,
                                   "time": datetime.now(timezone.utc).isoformat(timespec="seconds")})


def current_status(escalation_id: str) -> str | None:
    ups = [u for u in _rows("queue_updates.jsonl") if u["id"] == escalation_id]
    if ups:
        return ups[-1]["status"]
    row = get(escalation_id)
    return row["status"] if row else None
