"""Clinic-side monitoring rules (FICTIONAL demo thresholds, not clinical guidance).

This runs on the clinic side over ALL results, including ones not yet released
to the patient, the way a monitoring service sees new results as they arrive.
It must reproduce data/records/expected_alerts.csv exactly (see tests).
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import date, timedelta

import yaml

from . import config
from .records import RecordStore

INT_TESTS = {"ALT", "AST", "ALP", "GGT", "Platelets", "Sodium", "BUN", "Glucose",
             "Cholesterol Total", "LDL", "HDL", "Triglycerides"}
NSAIDS = ["ibuprofen", "naproxen", "diclofenac"]
WEAR_END = date.fromisoformat(config.WATCH_DATA_END)


@dataclass(frozen=True)
class Alert:
    patient_id: str
    rule_id: str
    priority: str
    trigger_date: str
    detail: str

    def as_dict(self) -> dict:
        return asdict(self)


def _fmt(test: str, raw: str) -> str:
    v = float(raw)
    return str(int(round(v))) if test in INT_TESTS else str(v)


class RulesEngine:
    def __init__(self, store: RecordStore, rules_path=config.RULES):
        self.store = store
        cfg = yaml.safe_load(open(rules_path, encoding="utf-8"))
        self.today = date.fromisoformat(cfg.get("today", config.TODAY))
        self.rules = {r["id"]: r for r in cfg["rules"]}

    def _alert(self, pid, rid, when, detail) -> Alert:
        return Alert(pid, rid, self.rules[rid]["priority"], when, detail)

    # ---------------------------------------------------------------- per-rule checks
    def check_message(self, pid: str, text: str, sent_date: str) -> Alert | None:
        terms = self.rules["R01_red_flag_message"]["terms"]
        hits = [t for t in terms if t in text.lower()]
        if hits:
            return self._alert(pid, "R01_red_flag_message", sent_date, f"message mentions: {', '.join(hits)}")
        return None

    def _labs_by_visit(self, pid: str) -> dict[int, dict[str, str]]:
        out: dict[int, dict[str, str]] = {}
        for r in self.store.labs:
            if r["patient_id"] == pid:
                out.setdefault(int(r["visit_no"]), {})[r["test"]] = r["value"]
        return out

    def _visit_dates(self, pid: str) -> dict[int, str]:
        return {int(v["visit_no"]): v["visit_date"] for v in self.store.visits if v["patient_id"] == pid}

    def _scores(self, pid: str) -> dict[int, dict]:
        return {int(s["visit_no"]): s for s in self.store.scores if s["patient_id"] == pid}

    def evaluate_patient(self, pid: str) -> list[Alert]:
        s = self.store
        alerts: list[Alert] = []
        # R01 red-flag messages
        for m in s.messages:
            if m["patient_id"] == pid:
                a = self.check_message(pid, m["message"], m["sent_date"])
                if a:
                    alerts.append(a)
        cirr, wear = s.is_cirrhosis(pid), s.has_wearable(pid)
        # R02 fluid gain (scale weight vs about 7 days earlier)
        if cirr and wear:
            w = {date.fromisoformat(r["date"]): float(r["weight_kg"]) for r in s.weights if r["patient_id"] == pid}
            for d in sorted(w):
                prev = [w[d - timedelta(days=j)] for j in range(7, 10) if d - timedelta(days=j) in w] or \
                       [w[d - timedelta(days=j)] for j in range(5, 7) if d - timedelta(days=j) in w]
                if prev and w[d] - prev[0] >= self.rules["R02_fluid_gain"]["threshold_kg"]:
                    alerts.append(self._alert(pid, "R02_fluid_gain", d.isoformat(),
                                              f"weight {w[d]} kg vs {prev[0]} kg about 7 days earlier"))
                    break
        # Lab and score rules, visit by visit
        labs, vdates, sc = self._labs_by_visit(pid), self._visit_dates(pid), self._scores(pid)
        n = max(labs)
        base = labs[1]
        for k in range(2, n + 1):
            d, prev, vd = labs[k], labs[k - 1], vdates[k]
            if cirr and int(sc[k]["meld3"]) - int(sc[k - 1]["meld3"]) >= self.rules["R03_meld_rise"]["threshold_points"]:
                alerts.append(self._alert(pid, "R03_meld_rise", vd,
                                          f"MELD 3.0 {sc[k - 1]['meld3']} to {sc[k]['meld3']} (visit {k})"))
            b, b0 = float(d["Bilirubin Total"]), float(base["Bilirubin Total"])
            if b >= 2 * b0 and b >= 2.0:
                alerts.append(self._alert(pid, "R04_bilirubin_double", vd,
                                          f"bilirubin {_fmt('Bilirubin Total', base['Bilirubin Total'])} to "
                                          f"{_fmt('Bilirubin Total', d['Bilirubin Total'])} mg/dL (visit {k})"))
            if float(prev["Platelets"]) >= 100 and float(d["Platelets"]) < 100:
                alerts.append(self._alert(pid, "R05_platelets_below_100", vd,
                                          f"platelets {_fmt('Platelets', prev['Platelets'])} to "
                                          f"{_fmt('Platelets', d['Platelets'])} (visit {k})"))
            if float(d["ALT"]) > 2 * float(base["ALT"]):
                alerts.append(self._alert(pid, "R07_alt_double", vd,
                                          f"ALT {_fmt('ALT', base['ALT'])} to {_fmt('ALT', d['ALT'])} U/L (visit {k})"))
            if float(d["A1c"]) >= 9.0:
                alerts.append(self._alert(pid, "R08_a1c_high", vd, f"A1c {_fmt('A1c', d['A1c'])}% (visit {k})"))
        # R06 NSAID on the list while the plan says no NSAIDs (cirrhosis plans)
        nsaids = [m for m in s.medications if m["patient_id"] == pid and m["active"] == "True" and m["medication"] in NSAIDS]
        if nsaids and cirr:
            alerts.append(self._alert(pid, "R06_nsaid_conflict", max(m["start_date"] for m in nsaids),
                                      f"{', '.join(m['medication'] for m in nsaids)} active while plan says No NSAIDs"))
        # R09 HCC surveillance ultrasound overdue
        if cirr:
            us = [date.fromisoformat(r["exam_date"]) for r in s.imaging if r["patient_id"] == pid]
            if us:
                lus = max(us)
                days = (self.today - lus).days
                if days > self.rules["R09_hcc_surveillance_overdue"]["max_days"]:
                    alerts.append(self._alert(pid, "R09_hcc_surveillance_overdue", self.today.isoformat(),
                                              f"last ultrasound {lus.isoformat()} ({days} days ago)"))
        # R10 low steps over the last 14 days (valid wear days only)
        if wear:
            r10 = self.rules["R10_low_steps"]
            start = WEAR_END - timedelta(days=r10["window_days"] - 1)
            valid = [int(r["steps"]) for r in s.wearables if r["patient_id"] == pid
                     and r["valid_wear_day"] == "True" and date.fromisoformat(r["date"]) >= start]
            if len(valid) >= r10["min_valid_days"] and sum(valid) / len(valid) < r10["threshold_steps"]:
                alerts.append(self._alert(pid, "R10_low_steps", WEAR_END.isoformat(),
                                          f"mean {int(sum(valid) / len(valid))} steps over {len(valid)} valid days"))
        # de-duplicate like the generator
        seen, out = set(), []
        for a in alerts:
            key = (a.patient_id, a.rule_id, a.trigger_date)
            if key not in seen:
                seen.add(key)
                out.append(a)
        return out

    def evaluate_all(self) -> list[Alert]:
        out = []
        for pid in sorted(self.store.patients):
            out.extend(self.evaluate_patient(pid))
        return sorted(out, key=lambda a: (a.patient_id, a.rule_id))
