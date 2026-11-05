# Model A

A patient-facing liver health assistant (Gen Academy course project). It answers a signed-in patient's
questions from their own health metrics (labs, scores, watch and scale data, medicines, care plan) and a
plain-language liver glossary, refuses everything else, and escalates red-flag symptoms to the care team.

> All data is FICTIONAL (30 synthetic patients). Never load real patient data into this project.

## Safety design

| Risk | How Model A handles it |
| --- | --- |
| Red-flag symptoms (GI bleeding, confusion, jaundice) | Detected by fixed rules before any model runs; fixed urgent message (call 911) plus one escalation; every later turn repeats it |
| Seeing another patient's data | `PatientView` is locked to one patient at session start; no method accepts a patient id; Pinecone note searches always filter by the session patient |
| Prompt injection hidden in notes | Notes are sanitized (hidden comments and instruction lines removed) before retrieval or the model |
| Unsafe or invented answers | Model answers only from cited context; output checker blocks dose changes, diagnoses, MRNs and other patient ids; one retry, then a safe template |
| Out-of-scope advice (diet, exercise, step targets) | Fixed "no information" answer pointing to the care team |
| Unreleased results | Patients see resulted values only; held-back results stay hidden until released |
| Emergency call goes wrong | Only fixed red-flag rules trigger it; number from .env allowlist only (never 911); dry run by default; one call per alert; hourly cap; minimal data; no recording; retry once then flag |
| Spoken answers drifting from written ones | Spoken version only shortens: any number not in the written answer sends it back to the rule-based version; fixed safety messages are spoken word for word |
| Results heard by others | Audio is off by default (Listen button); headphones reminder; spoken questions are shown as text before answering |
| Attacks (prompt injection, jailbreak, other-patient, PII, dose, diagnosis, malformed) | 25-case attack set in the evals and tests; all handled |
| Identifiers in logs | Names, MRNs, phones, emails, addresses scrubbed from traces, security log and audit log |
| Alerts reaching patients unchecked | Daily monitoring pauses every alert (LangGraph interrupt) until a clinician approves, edits or rejects; append-only audit log |
| Approved messages reaching the wrong patient | The patient page shows only approved or edited messages for the signed-in patient; rejected and pending alerts never appear (tested) |
| Tool misuse through MCP | Patient fixed at server start; all 8 tools read-only; no tool takes a patient id; local only |

## Clinician loop

1. Daily monitoring runs fixed rules on labs, scores, watch steps and weight (for example R07: ALT doubled; R10: under 2,000 steps a day over 14 days).
2. Each alert pauses in the Clinician queue with a **Patient summary**: latest labs and scores with previous values, 14-day steps and active minutes, 60-day weight change and current medicines. Read-only, no AI.
3. The clinician approves, edits or rejects the patient message. Every decision goes to the audit log.
4. Approved messages appear on the patient's chat page under **Messages from your care team**.

## How Model A was evaluated (Week 4 framework)

`python scripts/run_eval.py` runs the golden set (46) and the attack set (25), captures every trajectory to
`runs/agent_run_evals.csv` (expected vs actual tools, retrieved chunks, tool outputs, citations, final answer,
latency, tokens, cost) and writes `runs/eval_report.md`.

| Metric | Type | Offline result (template answers) |
| --- | --- | --- |
| Overall pass (golden) | rubric | 42/46 |
| Route accuracy | code | 46/46 |
| Red-flag recall | code | 6/6 (100%) |
| Refusal on forbidden inputs | code | 24/24 |
| Attack set handled | code | 25/25 |
| Identifier leaks | code | 0 |
| Tool-call accuracy | code | 1.00 |
| Citation accuracy | code | 0.95 |
| Context recall / precision (glossary) | code | 0.87 / 0.41 |
| Faithfulness, factual correctness | Nebius LLM judge | run with NEBIUS_API_KEY |

Pass rule: wrong route, tool trajectory or citation is an automatic fail; then thresholds on context recall,
faithfulness and factual correctness. Each row has empty `human_label`, `failure_category`, `human_comment`
columns for annotation and error analysis. Remaining failures: 4 glossary retrieval misses (expected entry not
in the top 3), kept visible on purpose.

## Cost

Every Nebius call records tokens, latency and cost (`src/model_a/llm.py`). The report shows measured cost per
question and a projection for 1,000 patients x 20 questions a month. Fixed safety replies (red flag, refusal,
out of scope) and glossary search (local BM25) cost $0. Prices default to $0.60 / $3.60 per 1M input/output
tokens for Qwen3.5-397B-A17B (third-party listing); set your own in `.env`.

## Project layout

```
data/            records (synthetic CSVs + notes), glossary, rules.yaml, golden set
src/model_a/
  records.py     RecordStore (clinic side) and PatientView (patient-scoped tools)
  rules.py       monitoring rules engine (reproduces expected_alerts.csv exactly)
  safety.py      red flags, note sanitizing, privacy, scope rule, output checks
  router.py      route each turn: red_flag, refuse_privacy, out_of_scope, clarify, answer
  context.py     gather cited facts from the patient's records and the glossary
  glossary.py    BM25 glossary search (or Pinecone with RETRIEVAL=pinecone)
  llm.py         Nebius Token Factory client (OpenAI-compatible)
  pipeline.py    the turn pipeline as plain functions
  graph.py       the same pipeline as a LangGraph graph (retry once, then stop)
  escalation.py  care-team queue, status history, urgent hooks
  voice.py       emergency voice caller (ElevenLabs + Twilio): allowlist, dry run, retry, flag
  mcp_server.py  read-only, patient-scoped MCP server (8 tools)
  speech.py      "Listen" layer: short spoken version, text to speech, speech to text
app.py           Streamlit chat page: type or speak a question, read or listen to the answer
  tracing.py     local JSONL trace, plus Langfuse when TRACING=on
scripts/         ask.py (chat), run_golden.py (evals), ingest.py (Pinecone),
                 test_call.py (voice demo), voice_webhook.py (post-call webhook)
docs/            voice_agent_setup.md (ElevenLabs agent prompt and setup)
tests/           hard-gate tests
```

## Setup (Windows, VS Code terminal)

```
cd %USERPROFILE%\Documents\model-a-app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```
Then open `.env` and paste your own keys. Keep `LLM_BACKEND=none` until the tests pass; it runs offline
with template answers. Set `LLM_BACKEND=nebius` and `NEBIUS_MODEL` to turn on the model.

## Run

```
python -m streamlit run app.py                        # chat page + Clinician queue page (left menu)
python scripts/run_eval.py                            # full evaluation -> runs/eval_report.md
python -m pytest -q                                   # hard-gate tests (35)
python scripts/run_golden.py                          # golden set -> runs/golden_results.csv
python scripts/ask.py --patient P13                   # chat as patient P13
python scripts/ask.py --patient P13 --graph           # same, through LangGraph
python scripts/ingest.py                              # build Pinecone index (then RETRIEVAL=pinecone)
python scripts/test_call.py --patient P20             # voice caller demo (VOICE_MODE decides dry run or live)
$env:MODEL_A_PATIENT_ID="P13"; python -m model_a.mcp_server --http   # MCP server, from the src folder
```

## Current results (offline, template answers)

- Rules engine: 20/20 expected alerts, 0 extra; no alerts for the 6 negative controls
- Patient tools: match every checked value in facts.csv
- Voice caller: red flags call once with minimal data; no calls for negative controls or injected notes;
  non-allowlisted and emergency numbers refused; retry once, then flagged
- Listen layer: every golden answer has a spoken version with no added numbers and no source tags
- MCP server: 8 read-only tools, none takes a patient id
- Router: 46/46 golden routes; red-flag recall 3/3; dark-stool negative control not escalated
- Glossary retrieval: expected entry in top 3 for 17/17 golden questions that cite one
- Note: the held-out rows were visible while the router and search were tuned, so add fresh held-out
  questions before reporting final numbers.

## Not built yet

Emergency phone call (code present, VOICE_MODE=off), mock hospital connection (FHIR), Pinecone and Langfuse
switched on, LangSmith dataset upload, fresh held-out golden questions, clinician sign-in (RBAC).
