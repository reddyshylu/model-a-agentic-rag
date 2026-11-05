"""Receive ElevenLabs post-call webhooks and decide: acknowledged, retry once, or flag.

    pip install fastapi uvicorn elevenlabs
    uvicorn scripts.voice_webhook:app --port 8080
ElevenLabs must reach this URL (e.g. through a tunnel during the demo). Every request
is signature-checked with ELEVENLABS_WEBHOOK_SECRET using the ElevenLabs SDK; unsigned
or wrongly signed requests are rejected.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI, HTTPException, Request  # noqa: E402

from model_a import config, voice  # noqa: E402
from model_a.records import RecordStore  # noqa: E402

app = FastAPI()
_store = RecordStore()
caller = voice.VoiceCaller(patient_ref=lambda pid: _store.patients[pid]["mrn"])


@app.post("/elevenlabs/post-call")
async def post_call(request: Request):
    if not config.ELEVENLABS_WEBHOOK_SECRET or config.ELEVENLABS_WEBHOOK_SECRET.startswith("your_"):
        raise HTTPException(503, "Set ELEVENLABS_WEBHOOK_SECRET first")
    body = (await request.body()).decode()
    sig = request.headers.get("elevenlabs-signature", "")
    try:
        from elevenlabs.client import ElevenLabs
        event = ElevenLabs(api_key=config.ELEVENLABS_API_KEY).webhooks.construct_event(
            rawBody=body, sig_header=sig, secret=config.ELEVENLABS_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(401, "Invalid signature")
    if not isinstance(event, dict):
        event = event.model_dump() if hasattr(event, "model_dump") else dict(event)
    return voice.handle_event(event, caller)
