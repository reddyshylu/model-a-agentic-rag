"""The "Listen" voice layer: a short spoken version of Model A's answer, read aloud.

Safety design:
- The spoken version only SHORTENS the written answer. Every number it says must
  appear in the written answer, or the safe rule-based version is used instead.
- Fixed messages (red flag, privacy, out of scope, clarify) are spoken word for word.
- Citations stay on screen; they are not read aloud.
- Without ElevenLabs settings nothing leaves the computer (audio is simply skipped).
"""
from __future__ import annotations

import json
import re
import urllib.request
import uuid
from datetime import date

from . import config, llm

TTS_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128"
STT_URL = "https://api.elevenlabs.io/v1/speech-to-text"
CLOSING = "Want to hear the rest, or send a question to your care team?"

UNITS = [("U/L", "units per liter"), ("mg/dL", "milligrams per deciliter"), ("g/dL", "grams per deciliter"),
         ("K/uL", "thousand per microliter"), ("mmol/L", "millimoles per liter"), ("ng/mL", "nanograms per milliliter"),
         ("steps/day", "steps a day"), ("min/week", "minutes a week"), ("dB/m", "decibels per meter"), ("kPa", "kilopascals"), (" kg", " kilograms"), ("%", " percent")]
SKIP = ("not released yet", config.CARE_TEAM_LINE)


def _speak_dates(text: str) -> str:
    def repl(m):
        d = date.fromisoformat(m.group(0))
        return f"{d.strftime('%B')} {d.day}, {d.year}"
    return re.sub(r"\b\d{4}-\d{2}-\d{2}\b", repl, text)


def _speak_numbers(text: str) -> str:
    return re.sub(r"\b(\d+)\.0\b", r"\1", text)  # 81.0 -> 81


def for_speech(text: str) -> str:
    """Remove citations and make units, dates and numbers easy to hear."""
    t = re.sub(r"\s*\[[^\]]+\]", "", text)
    t = _speak_dates(t)
    for a, b in UNITS:
        t = t.replace(a, b)
    return " ".join(_speak_numbers(t).split())


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def rule_based(written: str) -> str:
    """Up to 3 sentences, results with numbers first, then the closing question."""
    sents = [s for s in _sentences(re.sub(r"\s*\[[^\]]+\]", "", written)) if not any(k in s for k in SKIP)]
    with_numbers = [s for s in sents if re.search(r"\d", s)]
    rest = [s for s in sents if s not in with_numbers]
    picked = (with_numbers + rest)[: config.SPOKEN_MAX_POINTS]
    return for_speech(" ".join(picked) + " " + CLOSING)


def _numbers(text: str) -> set[float]:
    return {float(x) for x in re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))}


def check_spoken(spoken: str, written: str) -> list[str]:
    """Every number spoken must exist in the written answer (dates spoken as words are checked by day/year)."""
    allowed = _numbers(written) | _numbers(_speak_dates(written))
    extra = sorted(_numbers(spoken) - allowed)
    return [f"number not in written answer: {x:g}" for x in extra]


SHORTEN_PROMPT = """Shorten this answer for a patient to LISTEN to (about 20 seconds).
Rules: keep at most 3 points, most important or changed values first; use only facts and numbers from the
answer; do not add advice or new facts; no source tags; plain words; say units in full.
End with exactly: "{closing}"

ANSWER:
{answer}"""


def spoken_version(written: str, route: str) -> str:
    if route != "answer":
        return written  # fixed safety messages are spoken word for word
    if llm.available():
        try:
            draft = llm.chat([{"role": "user", "content": SHORTEN_PROMPT.format(closing=CLOSING, answer=written)}],
                             max_tokens=200)
            draft = for_speech(draft)
            if not check_spoken(draft, written):
                return draft
        except llm.LLMError:
            pass
    return rule_based(written)


# ---------------------------------------------------------------- ElevenLabs audio
def tts_available() -> bool:
    k = config.ELEVENLABS_API_KEY
    return bool(k) and not k.startswith("your_") and bool(config.ELEVENLABS_VOICE_ID) \
        and not config.ELEVENLABS_VOICE_ID.startswith("your_")


def text_to_speech(text: str) -> bytes | None:
    """MP3 bytes, or None when ElevenLabs is not configured or the call fails."""
    if not tts_available():
        return None
    req = urllib.request.Request(TTS_URL.format(voice_id=config.ELEVENLABS_VOICE_ID),
                                 data=json.dumps({"text": text, "model_id": config.ELEVENLABS_TTS_MODEL}).encode(),
                                 headers={"Content-Type": "application/json", "Accept": "audio/mpeg",
                                          "xi-api-key": config.ELEVENLABS_API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception:
        return None


def speech_to_text(audio: bytes, filename: str = "question.wav") -> str | None:
    """Transcribe a spoken question. None when not configured or on failure."""
    k = config.ELEVENLABS_API_KEY
    if not k or k.startswith("your_"):
        return None
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\n{config.ELEVENLABS_STT_MODEL}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
            f"Content-Type: application/octet-stream\r\n\r\n").encode() + audio + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(STT_URL, data=body, headers={
        "Content-Type": f"multipart/form-data; boundary={boundary}", "xi-api-key": k})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return (json.loads(resp.read()).get("text") or "").strip() or None
    except Exception:
        return None
