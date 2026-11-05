"""Plain-language liver glossary search.

Default: BM25 keyword search in pure Python (no account, works offline).
Optional: RETRIEVAL=pinecone uses the vector index built by scripts/ingest.py,
in the shared "glossary" namespace (no patient data lives there).
"""
from __future__ import annotations

import json
import math
import re
from collections import Counter
from functools import lru_cache

from . import config


STOPWORDS = set("""a an and are as at be bad been but by can could did do does doing for from go goes going good
had has have how i if in into is it its just me mean means meaning my of on or our so that the their them then
there these they this to up down was we were what when where which who why will with would you your am
should tell about any some more less much very really ok okay""".split())


# Everyday words patients use, mapped to the words the glossary uses (queries only).
SYNONYMS = {
    "steatosis": "fatty liver steatotic", "steatotic": "fatty liver", "fatty": "fatty liver",
    "scar": "scarring fibrosis", "scars": "scarring fibrosis", "scarred": "scarring fibrosis",
    "extract": "supplements herbal", "supplement": "supplements herbal", "herb": "herbal supplements",
    "losing": "loss", "lose": "loss", "lost": "loss",
    "poop": "stool", "stools": "stool", "tar": "black stool", "tarry": "black stool",
    "advil": "ibuprofen nsaids", "motrin": "ibuprofen nsaids", "aleve": "naproxen nsaids",
    "tylenol": "acetaminophen", "ev": "varices", "egd": "varices endoscopy",
    "difference": "ladder stages", "stages": "ladder stages", "worse": "ladder",
}


def stem(t: str) -> str:
    for suf in ("ing", "ed", "es", "s"):
        if t.endswith(suf) and len(t) - len(suf) >= 4 and not t.endswith(("ss", "is", "us")):
            return t[: -len(suf)]
    return t


def tokenize(s: str, expand: bool = False) -> list[str]:
    toks = [t for t in re.findall(r"[a-z0-9]+", s.lower()) if t not in STOPWORDS]
    if expand:
        toks = toks + [x for t in toks for x in SYNONYMS.get(t, "").split()]
    return [stem(t) for t in toks]


def entry_text(e: dict) -> str:
    """The searchable text of one entry (term and synonyms weighted 3x, as in the KB tests)."""
    return " ".join([(e["term"] + " ") * 3, (" ".join(e.get("also_known_as", [])) + " ") * 3,
                     e["what_it_is"], e["why_it_matters"], e["if_higher_or_worse"], e["if_lower_or_better"]])


class BM25:
    def __init__(self, docs: list[list[str]], k1: float = 1.5, b: float = 0.75):
        self.docs, self.k1, self.b = docs, k1, b
        self.avgdl = sum(len(d) for d in docs) / len(docs)
        self.tf = [Counter(d) for d in docs]
        df = Counter(t for d in docs for t in set(d))
        n = len(docs)
        self.idf = {t: math.log((n - f + 0.5) / (f + 0.5) + 1) for t, f in df.items()}

    def scores(self, query: list[str]) -> list[float]:
        out = []
        for d, tf in zip(self.docs, self.tf):
            s = 0.0
            for t in query:
                if t in tf:
                    f = tf[t]
                    s += self.idf[t] * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(d) / self.avgdl))
            out.append(s)
        return out


@lru_cache(maxsize=1)
def load_entries() -> list[dict]:
    with open(config.GLOSSARY, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


@lru_cache(maxsize=1)
def _index() -> BM25:
    return BM25([tokenize(entry_text(e)) for e in load_entries()])


def search(query: str, k: int = config.TOP_K, min_score: float = 2.0) -> list[dict]:
    """Return up to k glossary entries, each with a 'score'."""
    if config.RETRIEVAL == "pinecone":
        from .vectorstore import search_glossary  # optional dependency
        return search_glossary(query, k)
    entries = load_entries()
    scores = _index().scores(tokenize(query, expand=True))
    ranked = sorted(range(len(entries)), key=lambda i: -scores[i])[:k]
    return [{**entries[i], "score": round(scores[i], 2)} for i in ranked if scores[i] >= min_score]


def by_term(term: str) -> dict | None:
    t = term.lower()
    for e in load_entries():
        if e["term"].lower() == t or t in [a.lower() for a in e.get("also_known_as", [])]:
            return e
    return None
