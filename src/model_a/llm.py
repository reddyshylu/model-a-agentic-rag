"""Nebius Token Factory chat client (OpenAI-compatible), standard library only."""
from __future__ import annotations

import json
import time
import urllib.request

from . import config

# Every model call is metered here: tokens, latency, cost (read by pipeline and evals).
CALLS: list[dict] = []


def cost_usd(tokens_in: int, tokens_out: int) -> float:
    return tokens_in / 1e6 * config.PRICE_IN_PER_M + tokens_out / 1e6 * config.PRICE_OUT_PER_M


class LLMError(RuntimeError):
    pass


def available() -> bool:
    return config.LLM_BACKEND == "nebius" and bool(config.NEBIUS_API_KEY) \
        and not config.NEBIUS_API_KEY.startswith("your_") and bool(config.NEBIUS_MODEL)


def chat(messages: list[dict], max_tokens: int = config.LLM_MAX_TOKENS, model: str | None = None,
         purpose: str = "answer") -> str:
    if not available():
        raise LLMError("LLM not configured (set LLM_BACKEND=nebius, NEBIUS_API_KEY, NEBIUS_MODEL)")
    model = model or config.NEBIUS_MODEL
    body = json.dumps({"model": model, "messages": messages, "max_tokens": max_tokens,
                       "temperature": config.LLM_TEMPERATURE}).encode()
    req = urllib.request.Request(config.NEBIUS_BASE_URL.rstrip("/") + "/chat/completions", data=body,
                                 headers={"Content-Type": "application/json",
                                          "Authorization": f"Bearer {config.NEBIUS_API_KEY}"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=config.LLM_TIMEOUT_SECONDS) as resp:
            data = json.loads(resp.read())
        text = data["choices"][0]["message"]["content"] or ""
    except Exception as exc:
        CALLS.append({"purpose": purpose, "model": model, "ok": False,
                      "latency_ms": round((time.perf_counter() - t0) * 1000), "tokens_in": 0, "tokens_out": 0,
                      "cost_usd": 0.0})
        raise LLMError(f"Nebius call failed: {exc}") from exc
    u = data.get("usage") or {}
    tin, tout = int(u.get("prompt_tokens", 0)), int(u.get("completion_tokens", 0))
    CALLS.append({"purpose": purpose, "model": model, "ok": True,
                  "latency_ms": round((time.perf_counter() - t0) * 1000), "tokens_in": tin, "tokens_out": tout,
                  "cost_usd": cost_usd(tin, tout)})
    # Reasoning models may wrap thinking in <think> tags; never show that to the patient
    import re
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
