"""Daily monitoring with clinician approval (template step 8: human in the loop).

LangGraph flow per alert:  draft -> clinician_review (interrupt) -> finalize
- The rules engine (deterministic) finds alerts; nothing is decided by the LLM.
- Every alert pauses at clinician_review. Nothing reaches the patient until a
  clinician approves (optionally editing the patient message) or rejects it.
- Decisions are written to an append-only audit log.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, TypedDict

from . import config
from .records import RecordStore
from .redact import redact
from .rules import RulesEngine

PATIENT_TEMPLATES = {
    "urgent": "Your care team has reviewed a concerning message. Please call 911 or go to the emergency room if you have not already.",
    "high": "Your care team noticed a change in your recent results and will contact you soon to talk about next steps.",
    "medium": "Your care team noticed something in your recent results and will discuss it with you at your next contact.",
    "low": "Reminder from your care team: {detail_plain}",
}
LOW_PLAIN = {"R09_hcc_surveillance_overdue": "your liver ultrasound is due. Please call the clinic to schedule it.",
             "R10_low_steps": "your watch shows fewer steps than usual. Your care team may ask how you are doing."}


class AlertState(TypedDict, total=False):
    alert: dict
    draft_message: str
    decision: dict
    final: dict


def _audit(row: dict) -> None:
    config.ESCALATIONS.mkdir(parents=True, exist_ok=True)
    with open(config.ESCALATIONS / "clinician_audit.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                            **{k: redact(v) if isinstance(v, str) else v for k, v in row.items()}}) + "\n")


def draft(state: AlertState) -> AlertState:
    a = state["alert"]
    tmpl = PATIENT_TEMPLATES[a["priority"]]
    msg = tmpl.format(detail_plain=LOW_PLAIN.get(a["rule_id"], "please contact the clinic."))
    return {"draft_message": msg}


def clinician_review(state: AlertState) -> AlertState:
    from langgraph.types import interrupt
    decision = interrupt({"alert": state["alert"], "draft_message": state["draft_message"],
                          "options": ["approve", "edit", "reject"]})
    return {"decision": decision}


def finalize(state: AlertState) -> AlertState:
    d, a = state["decision"], state["alert"]
    action = d.get("action")
    if action not in ("approve", "edit", "reject"):
        raise ValueError("decision must be approve, edit or reject")
    message = d.get("message") if action == "edit" else state["draft_message"]
    final = {"alert_key": a["key"], "patient_id": a["patient_id"], "rule_id": a["rule_id"],
             "priority": a["priority"], "action": action, "clinician": d.get("clinician", "unknown"),
             "note": d.get("note", ""), "patient_message": None if action == "reject" else message}
    _audit(final)
    return {"final": final}


def build_monitor_graph(checkpointer=None):
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.graph import END, START, StateGraph
    g = StateGraph(AlertState)
    g.add_node("draft", draft)
    g.add_node("clinician_review", clinician_review)
    g.add_node("finalize", finalize)
    g.add_edge(START, "draft")
    g.add_edge("draft", "clinician_review")
    g.add_edge("clinician_review", "finalize")
    g.add_edge("finalize", END)
    return g.compile(checkpointer=checkpointer or MemorySaver())


class ClinicianQueue:
    """Runs monitoring and holds one paused LangGraph thread per alert."""

    def __init__(self, store: RecordStore | None = None):
        self.store = store or RecordStore()
        self.graph = build_monitor_graph()
        self.pending: dict[str, dict] = {}
        self.done: dict[str, dict] = {}

    def run_monitoring(self) -> list[dict]:
        new = []
        for al in RulesEngine(self.store).evaluate_all():
            a = al.as_dict()
            a["key"] = f"{a['patient_id']}-{a['rule_id']}-{a['trigger_date']}"
            if a["key"] in self.pending or a["key"] in self.done:
                continue
            cfg = {"configurable": {"thread_id": a["key"]}}
            out = self.graph.invoke({"alert": a}, cfg)
            payload = out["__interrupt__"][0].value
            self.pending[a["key"]] = {**payload, "config": cfg}
            new.append(payload)
        return new

    def decide(self, key: str, action: str, clinician: str, message: str = "", note: str = "") -> dict:
        from langgraph.types import Command
        item = self.pending.pop(key)
        out = self.graph.invoke(Command(resume={"action": action, "clinician": clinician,
                                                "message": message, "note": note}), item["config"])
        self.done[key] = out["final"]
        return out["final"]

    def sorted_pending(self) -> list[dict]:
        order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}
        return sorted(self.pending.values(), key=lambda p: (order[p["alert"]["priority"]], p["alert"]["patient_id"]))


# ---- Read-only views used by the Streamlit pages (no LLM, no writes)

SUMMARY_LABS = ("ALT", "AST", "Platelets", "A1c")


def patient_summary(store: RecordStore, pid: str) -> dict:
    """Side-by-side facts for the clinician: labs, scores, watch, weight, medicines.

    Uses the same patient-scoped PatientView as the chat tools, so it can only
    read this one patient's released records.
    """
    from datetime import date, timedelta
    v = store.for_patient(pid)
    labs = [s for s in (v.lab_summary(t) for t in SUMMARY_LABS) if s]
    scores = [s for s in (v.score_summary(n) for n in ("fib4", "meld3")) if s]
    weight = None
    rows = v.weights()
    if rows:
        last = rows[-1]
        cutoff = (date.fromisoformat(last["date"]) - timedelta(days=60)).isoformat()
        early = next((r for r in rows if r["date"] >= cutoff), rows[0])
        weight = {"latest_kg": float(last["weight_kg"]), "latest_date": last["date"],
                  "from_kg": float(early["weight_kg"]), "from_date": early["date"],
                  "change_kg": round(float(last["weight_kg"]) - float(early["weight_kg"]), 1)}
    meds = [f"{m['medication']} {m['dose']}" for m in v.medications()]
    return {"labs": labs, "scores": scores, "watch": v.watch_summary(), "weight": weight, "medications": meds}


def patient_messages(pid: str) -> list[dict]:
    """Approved or edited care-team messages for ONE patient, newest first.

    Rejected alerts never produce a message, and pending alerts are not in the
    audit log yet, so nothing reaches the patient before a clinician decides.
    """
    path = config.ESCALATIONS / "clinician_audit.jsonl"
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("patient_id") == pid and row.get("action") in ("approve", "edit") and row.get("patient_message"):
            out.append({"time": row.get("time", ""), "message": row["patient_message"], "rule_id": row.get("rule_id", "")})
    return sorted(out, key=lambda r: r["time"], reverse=True)
