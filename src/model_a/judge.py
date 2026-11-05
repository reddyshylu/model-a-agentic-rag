"""LLM-as-judge (Nebius) for the generation metrics in Arvind's Week 4 framework.

faithfulness:        share of claims in the answer supported by the retrieved context
factual_correctness: share of the reference points (must_include) the answer covers
Both return None when the model is not configured, so evals still run offline.
"""
from __future__ import annotations

import json
import re

from . import config, llm

FAITH_PROMPT = """You check an AI answer against its CONTEXT. Split the ANSWER into short factual claims
(ignore greetings and the sentence "Your care team can explain what this means for you.").
A claim is supported only if the CONTEXT states it or it directly follows; general medical knowledge does not count. For each claim decide if the CONTEXT supports it.
Reply with JSON only: {{"claims": [{{"claim": "...", "supported": true}}]}}

CONTEXT:
{context}

ANSWER:
{answer}"""

FACT_PROMPT = """REFERENCE lists the points a correct answer must contain, separated by semicolons.
For each point decide if the ANSWER states it (same meaning, numbers must match).
Reply with JSON only: {{"points": [{{"point": "...", "covered": true}}]}}

REFERENCE:
{reference}

ANSWER:
{answer}"""


def _json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, flags=re.S)
    return json.loads(m.group(0)) if m else {}


def faithfulness(answer: str, context: str) -> float | None:
    if not llm.available():
        return None
    try:
        out = _json(llm.chat([{"role": "user", "content": FAITH_PROMPT.format(context=context[:6000], answer=answer)}],
                             max_tokens=1200, model=config.JUDGE_MODEL, purpose="judge"))
        claims = out.get("claims", [])
        return round(sum(bool(c.get("supported")) for c in claims) / len(claims), 3) if claims else 1.0
    except Exception:
        return None


def factual_correctness(answer: str, reference: str) -> float | None:
    if not llm.available() or not reference.strip():
        return None
    try:
        out = _json(llm.chat([{"role": "user", "content": FACT_PROMPT.format(reference=reference, answer=answer)}],
                             max_tokens=1200, model=config.JUDGE_MODEL, purpose="judge"))
        pts = out.get("points", [])
        return round(sum(bool(p.get("covered")) for p in pts) / len(pts), 3) if pts else None
    except Exception:
        return None
