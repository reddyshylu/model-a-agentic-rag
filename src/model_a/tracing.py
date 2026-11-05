"""Tracing: always writes a local JSONL trace; also sends to Langfuse when TRACING=on."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import config
from .redact import redact_obj

_langfuse = None


def _client():
    global _langfuse
    if _langfuse is None and config.TRACING:
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse()
        except Exception:
            _langfuse = False
    return _langfuse or None


def record(name: str, data: dict) -> None:
    data = redact_obj(data)  # no names, MRNs, phones or emails in traces
    config.RUNS.mkdir(parents=True, exist_ok=True)
    row = {"time": datetime.now(timezone.utc).isoformat(timespec="seconds"), "name": name, **data}
    with open(config.RUNS / "trace.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row, default=str) + "\n")
    lf = _client()
    if lf:
        try:
            lf.trace(name=name, input=data.get("question"), output=data.get("answer"),
                     metadata={k: v for k, v in data.items() if k not in ("question", "answer")})
        except Exception:
            pass
