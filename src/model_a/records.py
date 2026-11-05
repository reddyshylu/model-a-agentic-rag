"""Synthetic patient records and the patient-scoped view.

Safety design:
- RecordStore holds every patient. Only the rules engine (clinic side) and
  PatientView use it directly.
- PatientView is bound to ONE patient id when the session starts. None of its
  methods accept a patient id, so nothing the model or the user types can make
  it return another patient's data.
- Patient-facing methods return resulted data only. Held-back (pending) results
  stay hidden until the demo "releases" them.
"""
from __future__ import annotations

import csv
import re
from datetime import date, timedelta
from pathlib import Path

from . import config

LAB_TESTS = ["ALT", "AST", "ALP", "GGT", "Bilirubin Total", "Albumin", "Total Protein", "INR",
             "Platelets", "WBC", "Hemoglobin", "Sodium", "Potassium", "BUN", "Creatinine",
             "Glucose", "A1c", "AFP", "Cholesterol Total", "LDL", "HDL", "Triglycerides"]
SCORE_NAMES = {"meld3": "MELD 3.0", "meld_na": "MELD-Na", "fib4": "FIB-4"}


def _read(root: Path, name: str) -> list[dict]:
    with open(root / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _num(x: str) -> float:
    return float(x)


def trend_word(first: float, last: float) -> str:
    """Same rule as the data generator: 5% band counts as about the same."""
    if last > first * 1.05:
        return "up"
    if last < first * 0.95:
        return "down"
    return "about the same"


class RecordStore:
    """All synthetic records, loaded from CSV files."""

    def __init__(self, root: Path = config.RECORDS):
        self.root = Path(root)
        self.patients = {r["patient_id"]: r for r in _read(self.root, "patients.csv")}
        self.labs = _read(self.root, "labs.csv")
        self.scores = _read(self.root, "scores.csv")
        self.visits = _read(self.root, "visits.csv")
        self.medications = _read(self.root, "medications.csv")
        self.allergies = _read(self.root, "allergies.csv")
        self.fibroscan = _read(self.root, "fibroscan.csv")
        self.imaging = _read(self.root, "imaging.csv")
        self.wearables = _read(self.root, "wearables_daily.csv")
        self.weights = _read(self.root, "weights_daily.csv")
        self.messages = _read(self.root, "messages.csv")
        self.notes_index = _read(self.root, "notes_index.csv")
        self._released: set[tuple[str, int]] = set()

    # ---- cohort facts used by the rules engine
    def is_cirrhosis(self, pid: str) -> bool:
        return self.patients[pid]["fibrosis_stage"] == "F4"

    def has_wearable(self, pid: str) -> bool:
        return self.patients[pid]["has_wearable"] == "True"

    # ---- demo release of held-back results (the "new result arrives" moment)
    def release(self, pid: str, visit_no: int) -> None:
        self._released.add((pid, int(visit_no)))

    def is_visible(self, row: dict) -> bool:
        if row.get("status", "resulted") == "resulted":
            return True
        return (row["patient_id"], int(row["visit_no"])) in self._released

    def for_patient(self, pid: str) -> "PatientView":
        if pid not in self.patients:
            raise KeyError(f"Unknown patient {pid}")
        return PatientView(self, pid)

    def name_index(self) -> dict[str, str]:
        """Lower-case full names and last names to patient id (privacy checks only)."""
        out = {}
        for pid, p in self.patients.items():
            out[f"{p['first_name']} {p['last_name']}".lower()] = pid
        return out


class PatientView:
    """Read-only, patient-scoped access. The patient id is fixed at construction."""

    def __init__(self, store: RecordStore, pid: str):
        self._store = store
        self._pid = pid

    @property
    def patient_id(self) -> str:
        return self._pid

    def _mine(self, rows: list[dict]) -> list[dict]:
        return [r for r in rows if r["patient_id"] == self._pid]

    # ---- profile
    def profile(self) -> dict:
        p = self._store.patients[self._pid]
        keep = ["first_name", "last_name", "diagnosis", "fibrosis_stage", "hepatology_clinician", "pcp",
                "health_literacy", "has_wearable"]
        return {k: p[k] for k in keep}

    # ---- labs
    def labs(self, test: str | None = None) -> list[dict]:
        rows = [r for r in self._mine(self._store.labs) if self._store.is_visible(r)]
        if test:
            rows = [r for r in rows if r["test"].lower() == test.lower()]
        return sorted(rows, key=lambda r: (int(r["visit_no"]), r["test"]))

    def lab_summary(self, test: str) -> dict | None:
        rows = self.labs(test)
        if not rows:
            return None
        first, last = rows[0], rows[-1]
        out = {
            "test": last["test"], "value": last["value"], "unit": last["unit"],
            "date": last["collected_date"], "flag": last["flag"],
            "ref_low": last["ref_low"], "ref_high": last["ref_high"],
            "source": f"labs visit {last['visit_no']}",
        }
        if len(rows) >= 2:
            out["previous"] = rows[-2]["value"]
            out["first"] = first["value"]
            out["trend"] = trend_word(_num(first["value"]), _num(last["value"]))
        return out

    def pending_results(self) -> list[str]:
        """Names of tests drawn but not yet released (no values)."""
        rows = [r for r in self._mine(self._store.labs) if not self._store.is_visible(r)]
        return sorted({r["test"] for r in rows})

    # ---- scores
    def scores(self) -> list[dict]:
        rows = [r for r in self._mine(self._store.scores) if self._store.is_visible(r)]
        return sorted(rows, key=lambda r: int(r["visit_no"]))

    def score_summary(self, name: str) -> dict | None:
        rows = self.scores()
        if not rows:
            return None
        out = {"score": SCORE_NAMES[name], "value": rows[-1][name], "source": f"scores visit {rows[-1]['visit_no']}"}
        if len(rows) >= 2:
            out["previous"] = rows[-2][name]
        return out

    # ---- imaging and FibroScan
    def fibroscan(self) -> list[dict]:
        return sorted(self._mine(self._store.fibroscan), key=lambda r: int(r["visit_no"]))

    def imaging(self) -> list[dict]:
        return sorted(self._mine(self._store.imaging), key=lambda r: r["exam_date"])

    def ultrasound_status(self) -> dict | None:
        us = [r for r in self.imaging() if "ultrasound" in r["exam"].lower()]
        if not us:
            return None
        last = date.fromisoformat(us[-1]["exam_date"])
        out = {"last_ultrasound": last.isoformat(), "impression": us[-1]["impression"]}
        if self._store.is_cirrhosis(self._pid):  # HCC surveillance every 6 months
            due = last + timedelta(days=182)
            out["next_due"] = due.isoformat()
            out["overdue"] = due < date.fromisoformat(config.TODAY)
        return out

    # ---- medicines
    def medications(self, active_only: bool = True) -> list[dict]:
        rows = self._mine(self._store.medications)
        return [r for r in rows if r["active"] == "True"] if active_only else rows

    def allergies(self) -> list[dict]:
        return self._mine(self._store.allergies)

    # ---- watch and scale
    def watch_summary(self, days: int = 14) -> dict | None:
        rows = self._mine(self._store.wearables)
        if not rows:
            return None
        end = date.fromisoformat(config.WATCH_DATA_END)
        start = end - timedelta(days=days - 1)
        valid = [r for r in rows if r["valid_wear_day"] == "True" and date.fromisoformat(r["date"]) >= start]
        if not valid:
            return {"valid_days": 0, "start": start.isoformat(), "end": end.isoformat()}
        sleep = [float(r["sleep_hours"]) for r in valid if r["sleep_hours"]]
        return {
            "start": start.isoformat(), "end": end.isoformat(), "valid_days": len(valid),
            "avg_steps": int(sum(int(r["steps"]) for r in valid) / len(valid)),
            "avg_active_min": round(sum(int(r["active_min_moderate_plus"]) for r in valid) / len(valid)),
            "avg_sleep_hours": round(sum(sleep) / len(sleep), 1) if sleep else None,
            "source": "watch data",
        }

    def weights(self) -> list[dict]:
        return sorted(self._mine(self._store.weights), key=lambda r: r["date"])

    def weight_summary(self) -> dict | None:
        rows = self.weights()
        if not rows:
            return None
        latest = rows[-1]
        d = date.fromisoformat(latest["date"])
        week = None
        for j in (7, 8, 6, 9, 5):  # nearest reading about a week earlier
            hit = [r for r in rows if r["date"] == (d - timedelta(days=j)).isoformat()]
            if hit:
                week = hit[0]
                break
        out = {"latest_kg": latest["weight_kg"], "latest_date": latest["date"], "source": "home scale"}
        if week:
            out["week_ago_kg"] = week["weight_kg"]
            out["week_ago_date"] = week["date"]
        return out

    # ---- visit notes (sanitized before anything sees them)
    def notes(self) -> list[dict]:
        return sorted(self._mine(self._store.notes_index), key=lambda r: int(r["visit_no"]))

    def note_text(self, visit_no: int) -> str | None:
        from .safety import sanitize_note  # local import avoids a cycle
        for r in self.notes():
            if int(r["visit_no"]) == int(visit_no):
                raw = (self._store.root / r["note_file"]).read_text(encoding="utf-8")
                return sanitize_note(raw)
        return None

    def care_plan(self) -> dict | None:
        notes = self.notes()
        if not notes:
            return None
        last = notes[-1]
        text = self.note_text(int(last["visit_no"])) or ""
        m = re.search(r"## Assessment and Plan\n(.*)", text, flags=re.S)
        plan = m.group(1).strip() if m else ""
        lines = [ln.strip("- ").strip() for ln in plan.splitlines()
                 if ln.strip().startswith("-") or ln.strip().startswith("**")]
        return {"visit_date": last["visit_date"], "lines": lines, "source": f"note visit {last['visit_no']}"}
