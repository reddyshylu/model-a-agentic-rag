"""Gather cited facts for an answer. Every item carries a source tag the answer must cite."""
from __future__ import annotations

import re

from . import glossary
from .records import PatientView
from .router import Route


TOOL_FOR_SOURCE = [  # source tag prefix -> the read-only tool that produced it
    ("glossary", "search_glossary"), ("labs", "get_labs"), ("scores", "get_scores"),
    ("FibroScan", "get_imaging"), ("ultrasound", "get_imaging"), ("medications", "get_medications"),
    ("care plan", "get_care_plan"), ("watch data", "get_watch_summary"), ("home scale", "get_weight_summary"),
    ("visit notes", "read_note"), ("note visit", "read_note"), ("latest note", "read_note"),
    ("allergies", "get_allergies"),
]


def tool_for(source: str) -> str:
    if source.startswith(("labs pending", "safety")):
        return "other"  # notices from the pipeline, not tool calls
    return next((t for p, t in TOOL_FOR_SOURCE if source.startswith(p)), "other")


def _item(src: str, plain: str, detail: str | None = None) -> dict:
    return {"source": src, "plain": plain, "detail": detail or plain, "tool": tool_for(src)}


def _range(s: dict) -> str:
    if s["ref_low"] and s["ref_high"]:
        return f"lab range {s['ref_low']} to {s['ref_high']}"
    return "no lab range given"


def lab_items(pv: PatientView, tests: list[str]) -> list[dict]:
    out = []
    for t in tests:
        s = pv.lab_summary(t)
        if not s:
            out.append(_item(f"labs {t}", f"I don't see a resulted {t} test in your records."))
            continue
        flag = {"H": "above the lab range", "L": "below the lab range"}.get(s["flag"], "within the lab range")
        plain = f"Your latest {t} was {s['value']} {s['unit']} on {s['date']}, {flag}."
        if "trend" in s:
            plain += f" Since your first visit it went {s['trend']} ({s['first']} to {s['value']})." \
                if s["trend"] != "about the same" else f" It is about the same as at your first visit ({s['first']} to {s['value']})."
        out.append(_item(f"labs {t}", plain, plain + f" ({_range(s)}; {s['source']})"))
    return out


def gather(route: Route, pv: PatientView, question: str) -> list[dict]:
    items: list[dict] = []
    low = question.lower()
    items += lab_items(pv, route.labs)

    for sc in route.scores:
        s = pv.score_summary(sc)
        if s:
            plain = f"Your latest {s['score']} score is {s['value']}"
            plain += f" (the time before it was {s['previous']})." if "previous" in s else "."
            items.append(_item(f"scores {s['score']}", plain, plain + f" ({s['source']})"))

    t = route.topics
    if "fibroscan" in t:
        fs = pv.fibroscan()
        if fs:
            f = fs[-1]
            items.append(_item("FibroScan", f"Your latest FibroScan on {f['exam_date']} showed stiffness "
                                            f"{f['stiffness_kpa']} kPa and CAP {f['cap_db_m']} dB/m."))
    if "ultrasound" in t:
        u = pv.ultrasound_status()
        if u:
            plain = f"Your last liver ultrasound was on {u['last_ultrasound']}."
            if "next_due" in u:
                plain += f" The next one was due by {u['next_due']}"
                plain += ", so it is overdue. Please contact the clinic to schedule it." if u["overdue"] else "."
            items.append(_item("ultrasound", plain, plain + f" Result: {u['impression']}"))
            plan = pv.care_plan()
            us_lines = [ln for ln in (plan["lines"] if plan else []) if re.search(r"\bUS\b|ultrasound", ln)]
            if us_lines:
                items.append(_item(f"care plan ({plan['visit_date']})", f"Your care plan says: {us_lines[0]}."))
    if "meds" in t or "nsaid" in t or "supplement" in t:
        meds = pv.medications()
        if route.med_names:
            for m in [x for x in pv.medications(active_only=False) if x["medication"] in route.med_names]:
                items.append(_item(f"medications {m['medication']}",
                                   f"Your list shows {m['medication']} {m['dose']}: \"{m['sig']}\", started {m['start_date']}."
                                   + ("" if m["active"] == "True" else f" It was stopped on {m['stop_date']}.")))
        elif "meds" in t:
            names = "; ".join(f"{m['medication']} {m['dose']}" for m in meds)
            items.append(_item("medications", f"Your current medicine list: {names}."))
        if "supplement" in t:
            sup = [m for m in meds if re.search(r"extract|supplement|herbal|tea", (m["medication"] + " " + m["note"]).lower())]
            for m in sup:
                items.append(_item(f"medications {m['medication']}",
                                   f"Your list shows you started {m['medication']} on {m['start_date']}."))
    if "nsaid" in t:
        ns = [m for m in pv.medications() if m["medication"] in ("ibuprofen", "naproxen", "diclofenac")]
        plan = pv.care_plan()
        no_nsaid = plan and any("no nsaid" in ln.lower() for ln in plan["lines"])
        if no_nsaid:
            items.append(_item(f"care plan ({plan['visit_date']})", "Your care plan says: no NSAIDs (such as ibuprofen or naproxen)."))
        if ns:
            items.append(_item("medications", f"Your medicine list also shows {', '.join(m['medication'] for m in ns)}. "
                                              "Please ask your care team before taking or stopping it."))
    if "watch" in t:
        w = pv.watch_summary()
        if w and w.get("valid_days"):
            items.append(_item("watch data", f"From {w['start']} to {w['end']}, you averaged about {w['avg_steps']:,} steps a day "
                                             f"on the {w['valid_days']} days you wore your watch."
                                             + (f" Average sleep was {w['avg_sleep_hours']} hours." if w["avg_sleep_hours"] else "")))
        elif w is None:
            items.append(_item("watch data", "I don't see watch data connected to your record."))
        plan = pv.care_plan()
        goal = [ln for ln in (plan["lines"] if plan else []) if "steps" in ln.lower()]
        if goal:
            items.append(_item(f"care plan ({plan['visit_date']})", f"Your care plan says: {goal[0]}."))
    if "weight" in t:
        ws = pv.weight_summary()
        if ws:
            plain = f"Your latest scale weight was {ws['latest_kg']} kg on {ws['latest_date']}."
            if "week_ago_kg" in ws:
                plain += f" About a week earlier ({ws['week_ago_date']}) it was {ws['week_ago_kg']} kg."
            items.append(_item("home scale", plain))
    if "stage" in t:
        p = pv.profile()
        items.append(_item("visit notes", f"Your notes list {p['diagnosis']} with fibrosis stage {p['fibrosis_stage']}."))
    if "care_plan" in t:
        plan = pv.care_plan()
        if plan:
            items.append(_item(f"care plan ({plan['visit_date']})", "Your latest care plan includes: "
                               + "; ".join(plan["lines"][:8]) + "."))
    if "allergies" in t:
        al = pv.allergies()
        items.append(_item("allergies", "Your allergy list: " + ("; ".join(f"{a['allergen']} ({a['reaction']})" for a in al) or "none") + "."))
    if "note" in t:
        notes = pv.notes()
        want = 1 if "first" in low else int(notes[-1]["visit_no"])
        text = pv.note_text(want) or ""
        keep = re.search(r"## History of Present Illness\n(.*?)\n## ", text, flags=re.S)
        plan = re.search(r"## Assessment and Plan\n(.*)", text, flags=re.S)
        body = ((keep.group(1).strip() + "\n") if keep else "") + (plan.group(1).strip()[:1200] if plan else "")
        items.append(_item(f"note visit {want}", f"Notes from visit {want}.", body))
    if "changes" in t:
        items += change_items(pv)
    if route.labs or route.scores or "changes" in t:
        pend = pv.pending_results()
        if pend:
            items.append(_item("labs pending", "Some results from your most recent visit are not released yet, "
                                               "so they are not included here."))

    symptom = re.search(r"\b(stool|stools|poop|urine|pee)\b", low)
    if symptom and not route.labs and not route.scores:
        items.append(_item("safety check", "This is not one of the urgent warning signs Model A watches for. "
                                           "If you are worried, or it does not go away, ask your care team."))
        return items
    if "education" in route.tags or "safety" in route.tags:
        q = question + " " + " ".join(route.labs + route.topics)
        for e in glossary.search(q, k=3):
            detail = f"{e['term']}: {e['what_it_is']} {e['why_it_matters']} If higher or worse: {e['if_higher_or_worse']} " \
                     f"If lower or better: {e['if_lower_or_better']}"
            it = _item(f"glossary {e['id']}", f"{e['term']}: {e['what_it_is']}", detail)
            it["retrieval_score"] = e.get("score")
            items.append(it)
    return items


def change_items(pv: PatientView) -> list[dict]:
    labs = pv.labs()
    visits = sorted({int(r["visit_no"]) for r in labs})
    if len(visits) < 2:
        return [_item("labs", "There is only one visit with released results, so there is nothing to compare yet.")]
    a, b = visits[-2], visits[-1]
    prev = {r["test"]: r for r in labs if int(r["visit_no"]) == a}
    cur = {r["test"]: r for r in labs if int(r["visit_no"]) == b}
    lines = []
    for test, r in cur.items():
        if test in prev:
            x, y = float(prev[test]["value"]), float(r["value"])
            if x and abs(y - x) / abs(x) >= 0.10:
                lines.append(f"{test} {prev[test]['value']} to {r['value']} {r['unit']}")
    date_b = next(iter(cur.values()))["collected_date"]
    plain = f"Comparing your last two released lab visits (latest {date_b}), these changed by 10% or more: " + \
            ("; ".join(lines) if lines else "none") + "."
    out = [_item(f"labs visits {a} and {b}", plain)]
    sc = pv.scores()
    if len(sc) >= 2:
        x, y = sc[-2], sc[-1]
        out.append(_item(f"scores visits {x['visit_no']} and {y['visit_no']}",
                         f"Scores: MELD 3.0 {x['meld3']} to {y['meld3']}, FIB-4 {x['fib4']} to {y['fib4']}."))
    notes = pv.notes()
    if notes:
        last = notes[-1]
        plan = pv.care_plan()
        out.append(_item(f"latest note visit {last['visit_no']}",
                         f"Your latest visit note is from {last['visit_date']}."
                         + (f" Plan items include: {'; '.join(plan['lines'][:4])}." if plan else "")))
    return out
