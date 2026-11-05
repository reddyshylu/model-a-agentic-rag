"""Remove personal identifiers before anything is written to traces, logs or Langfuse.

Patient IDs (P01 to P30) stay, so runs can still be debugged; names, MRNs,
phone numbers, emails, addresses and dates of birth are replaced.
"""
from __future__ import annotations

import re
from functools import lru_cache

PATTERNS = [
    (re.compile(r"\bLW-\d{7}\b"), "[REDACTED_MRN]"),
    (re.compile(r"\(?\b\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"), "[REDACTED_PHONE]"),
    (re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"), "[REDACTED_EMAIL]"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b(?=.{0,20}\b(born|dob|birth))", re.I), "[REDACTED_DOB]"),
]


@lru_cache(maxsize=1)
def _known_values() -> list[tuple[re.Pattern, str]]:
    """Names and addresses of the fictional cohort, longest first."""
    try:
        from .records import RecordStore
        pts = RecordStore().patients.values()
    except Exception:
        return []
    vals = set()
    for p in pts:
        vals.update([p["first_name"], p["last_name"], p["address"], p["emergency_contact"].split(" (")[0]])
    vals = sorted((v for v in vals if v and len(v) > 2), key=len, reverse=True)
    return [(re.compile(rf"\b{re.escape(v)}\b", re.I), "[REDACTED_NAME]") for v in vals]


def redact(text):
    if not isinstance(text, str):
        return text
    for pat, rep in PATTERNS:
        text = pat.sub(rep, text)
    for pat, rep in _known_values():
        text = pat.sub(rep, text)
    return text


def redact_obj(obj):
    if isinstance(obj, str):
        return redact(obj)
    if isinstance(obj, dict):
        return {k: redact_obj(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [redact_obj(v) for v in obj]
    return obj
