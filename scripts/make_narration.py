"""Make the video narration with your ElevenLabs voice (runs on your computer; the key stays here).

    python scripts/make_narration.py
Writes docs/video/s01_title.mp3 ... s10_close.mp3 using ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID from .env.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from model_a import config  # noqa: E402

OUT = ROOT / "docs" / "video"
scenes = json.loads((OUT / "narration.json").read_text(encoding="utf-8"))
if not config.ELEVENLABS_API_KEY or config.ELEVENLABS_API_KEY.startswith("your_"):
    sys.exit("Set ELEVENLABS_API_KEY in .env first.")
url = f"https://api.elevenlabs.io/v1/text-to-speech/{config.ELEVENLABS_VOICE_ID}?output_format=mp3_44100_128"
for s in scenes:
    dest = OUT / f"{s['id']}.mp3"
    if dest.exists() and dest.stat().st_size > 1000:
        print("already done:", dest.name)
        continue
    body = json.dumps({"text": s["text"], "model_id": "eleven_multilingual_v2",
                       "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", "Accept": "audio/mpeg",
                                                          "xi-api-key": config.ELEVENLABS_API_KEY})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            dest.write_bytes(r.read())
        print("made:", dest.name)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs refused {s['id']} ({e.code}): {e.read().decode()[:300]}")
    time.sleep(0.5)
print("All narration files are in", OUT)
