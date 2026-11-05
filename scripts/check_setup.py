"""Show what Model A sees (keys are never printed) and make one tiny Nebius test call.

    python scripts/check_setup.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a import config, llm  # noqa: E402


def show_key(v):
    if not v or v.startswith("your_"):
        return "NOT SET"
    return f"set ({len(v)} characters)"


print("Python:", sys.executable)
print(".env found:", (config.ROOT / ".env").exists(), "at", config.ROOT / ".env")
print("LLM_BACKEND:", config.LLM_BACKEND)
print("NEBIUS_MODEL:", config.NEBIUS_MODEL or "NOT SET")
print("NEBIUS_BASE_URL:", config.NEBIUS_BASE_URL)
print("NEBIUS_API_KEY:", show_key(config.NEBIUS_API_KEY))
print("ELEVENLABS_API_KEY:", show_key(config.ELEVENLABS_API_KEY))
print("Model ready:", llm.available())
if llm.available():
    try:
        out = llm.chat([{"role": "user", "content": "Reply with the single word: ready"}], max_tokens=20, purpose="check")
        c = llm.CALLS[-1]
        print(f"Nebius test call OK: '{out[:40]}' | {c['latency_ms']} ms | {c['tokens_in']}+{c['tokens_out']} tokens")
    except Exception as e:
        print("Nebius test call FAILED:", str(e)[:300])

# List the chat models this key can use (helps fix "404 Not Found" = wrong NEBIUS_MODEL)
if config.NEBIUS_API_KEY and not config.NEBIUS_API_KEY.startswith("your_"):
    import json
    import urllib.request
    try:
        req = urllib.request.Request(config.NEBIUS_BASE_URL.rstrip("/") + "/models",
                                     headers={"Authorization": f"Bearer {config.NEBIUS_API_KEY}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            ids = sorted(m["id"] for m in json.loads(r.read()).get("data", []))
        wanted = [i for i in ids if any(w in i.lower() for w in ("qwen", "llama", "deepseek", "gpt-oss", "mistral"))]
        print(f"\nModels your key can use ({len(ids)} total). Chat models:")
        for i in wanted:
            print("  ", i)
        if config.NEBIUS_MODEL not in ids:
            print(f"\nNEBIUS_MODEL '{config.NEBIUS_MODEL}' is NOT in this list. Copy one name above into .env line NEBIUS_MODEL=")
    except Exception as e:
        print("Could not list models:", str(e)[:200])
