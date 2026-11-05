"""Deterministic guardrails that run before and after the model.

These are plain rules on purpose: red flags need 100% recall, so they must not
depend on an LLM's mood. The LLM only writes answers for questions that pass.
"""
from __future__ import annotations

import re
from functools import lru_cache

import yaml

from . import config

# ---------------------------------------------------------------- red flags
# The clinic rule R01 terms plus common everyday wordings of the same symptoms.
EXTRA_RED_FLAG_TERMS = [
    "throwing up blood", "threw up blood", "bloody vomit", "vomit blood", "puking blood",
    "blood in my stool", "bloody stool", "maroon stool", "black tarry", "tarry stool",
    "poop is black", "poop looks black", "stool is black", "stools are black",
    "yellow skin", "skin is yellow", "skin looks yellow", "turning yellow",
    "can't stay awake", "cannot stay awake", "very sleepy and confused", "disoriented",
    "passed out", "fainted", "belly is swelling", "stomach is swelling fast",
]


@lru_cache(maxsize=1)
def red_flag_terms() -> list[str]:
    rules = yaml.safe_load(config.RULES.read_text(encoding="utf-8"))
    r01 = next(r for r in rules["rules"] if r["id"] == "R01_red_flag_message")
    return [t.lower() for t in r01["terms"]] + EXTRA_RED_FLAG_TERMS


def detect_red_flag(text: str) -> list[str]:
    """Return the red-flag terms found in a patient message (empty list if none)."""
    low = " ".join(text.lower().split())
    return [t for t in red_flag_terms() if t in low]


# ---------------------------------------------------------------- prompt injection in notes
INJECTION_PATTERNS = [
    r"<!--.*?-->",  # hidden HTML comments
    r"(?im)^.*\b(ignore|disregard|forget)\b.{0,40}\b(previous|prior|above|all)\b.{0,40}\binstructions?\b.*$",
    r"(?im)^.*\b(system note|system prompt|you are now|act as)\b.*$",
]


def sanitize_note(text: str) -> str:
    """Remove hidden or instruction-like lines from a visit note before any model sees it."""
    out = text
    for pat in INJECTION_PATTERNS:
        out = re.sub(pat, "", out, flags=re.S if pat.startswith("<!--") else 0)
    return out


def looks_like_injection(text: str) -> bool:
    return any(re.search(p, text, flags=re.S | re.I) for p in INJECTION_PATTERNS)


# ---------------------------------------------------------------- privacy
OTHER_PERSON_PATTERNS = [
    r"\b(someone else|another patient|other patients?|all patients|every patient|everyone's)\b",
    r"\b(my|his|her)\s+(husband|wife|son|daughter|mother|father|mom|dad|friend|partner|brother|sister)'?s?\s+(labs?|results?|records?|chart|data)\b",
    r"\b(admin|developer|debug|god) mode\b",
    r"\b(patients|users) table\b|\bdatabase\b|\ball (the )?records\b|\bdump\b",
]
# Identifiers are never read out in chat (data minimization), even the patient's own.
IDENTIFIER_PATTERNS = [
    r"\bmrn\b|medical record number|\bssn\b|social security",
    r"\b(home )?address\b|\bphone number\b|emergency contact|\bdate of birth\b|\bdob\b|\bemail\b",
]


def detect_identifier_request(text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in IDENTIFIER_PATTERNS)


def detect_privacy(text: str, other_names: list[str], own_id: str = "") -> bool:
    """True when the message asks for someone else's records."""
    low = text.lower()
    if [p for p in re.findall(r"\bp\d{2}\b", low) if p.upper() != own_id.upper()]:
        return True
    if any(re.search(p, low) for p in OTHER_PERSON_PATTERNS):
        return True
    return any(name in low for name in other_names)


# ---------------------------------------------------------------- scope rule
# Model A answers only from health metrics and the glossary. Advice on diet,
# drinks, exercise type, workout style, heart rate while walking, step targets
# and anything unrelated gets the fixed "no information" answer.
OUT_OF_SCOPE_PATTERNS = [
    r"\b(sugar|soda|coffee|alcohol|beer|wine|diet|food|foods|eat|eating|meal|meals|drink|drinks|juice|keto|fasting|carbs?|recipe)\b",
    r"\b(exercise|exercises|workout|work out|gym|yoga|running|lift|lifting|training)\b",
    r"\bheart ?(rate|beat)\b",
    r"\b(how many|how much)\s+steps\s+(do|should)\b",
    r"\bsteps?\s+(should|do i need|target|goal)\b",
    r"\b(weather|news|stock|sports|movie|recipe|joke)\b",
]
# These keep a question in scope even if it mentions food or drink words.
IN_SCOPE_OVERRIDES = [
    r"\b(supplement|extract|vitamin|herbal|medicine|medication|pill|tablet|dose)\b",
    r"\b(steps did i|my steps|steps have i|did i walk|have i walked)\b",
    r"\b(ibuprofen|advil|motrin|naproxen|aleve|tylenol|acetaminophen)\b",
    r"\b(stool|stools|poop|urine|pee|skin|eyes)\b",  # symptom questions stay in scope
    r"\b(blood sugar|sugar is high|sugar level|sugar levels|my sugar)\b",  # a metric, not diet advice
]


def detect_out_of_scope(text: str) -> bool:
    low = text.lower()
    if any(re.search(p, low) for p in IN_SCOPE_OVERRIDES):
        return False
    return any(re.search(p, low) for p in OUT_OF_SCOPE_PATTERNS)


# ---------------------------------------------------------------- output checks (after the model)
UNSAFE_OUTPUT_PATTERNS = [
    r"\b(increase|decrease|double|stop|skip)\s+(your|the)\s+(dose|medicine|medication|insulin|metformin)\b",
    r"\byou (have|probably have|likely have) (cancer|cirrhosis|hcc)\b",
    r"\bnothing to worry about\b",
    r"\byou (don't|do not) need to (see|call) (a|your) (doctor|care team)\b",
]


def check_output(answer: str, patient_ids_other: list[str]) -> list[str]:
    """Return a list of problems found in a drafted answer (empty means it passes)."""
    problems = []
    low = answer.lower()
    for p in UNSAFE_OUTPUT_PATTERNS:
        if re.search(p, low):
            problems.append(f"unsafe phrase: {p}")
    for other in patient_ids_other:
        if re.search(rf"\b{re.escape(other.lower())}\b", low):
            problems.append(f"mentions another patient id {other}")
    if re.search(r"\bLW-\d{7}\b", answer):
        problems.append("contains an MRN")
    return problems
