"""Run the golden set and write runs/golden_results.csv plus a summary.

    python scripts/run_golden.py            # all rows
    python scripts/run_golden.py --split dev
Follow-up rows replay their parent turns first, in the same session.
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a import config  # noqa: E402
from model_a.pipeline import ModelA  # noqa: E402


def primary(expected: str) -> str:
    return "answer" if expected.startswith(("record", "education")) else expected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", choices=["dev", "held_out"])
    a = ap.parse_args()
    rows = list(csv.DictReader(open(config.GOLDEN, encoding="utf-8")))
    by_id = {r["id"]: r for r in rows}
    if a.split:
        rows = [r for r in rows if r["split"] == a.split]
    model, out = ModelA(), []
    for r in rows:
        s = model.start_session(r["patient_id"])
        chain, cur = [], r
        while cur["follows_up_on"]:
            cur = by_id[cur["follows_up_on"]]
            chain.insert(0, cur)
        for c in chain:
            model.ask(s, c["question"])
        ans = model.ask(s, r["question"])
        out.append({"id": r["id"], "split": r["split"], "patient_id": r["patient_id"], "question": r["question"],
                    "expected_route": r["expected_route"], "got_route": ans.route,
                    "route_ok": ans.route == primary(r["expected_route"]), "sources": "; ".join(ans.sources),
                    "expected_sources": r["expected_sources"], "must_include": r["must_include"],
                    "must_not": r["must_not"], "answer": ans.text, "problems": "; ".join(ans.problems),
                    "llm_used": ans.llm_used, "human_label": "", "failure_note": ""})
    config.RUNS.mkdir(exist_ok=True)
    path = config.RUNS / "golden_results.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    ok = sum(o["route_ok"] for o in out)
    rf = [o for o in out if o["expected_route"] == "red_flag"]
    print(f"rows {len(out)} | route accuracy {ok}/{len(out)} | "
          f"red-flag recall {sum(o['got_route'] == 'red_flag' for o in rf)}/{len(rf)} | "
          f"answers with output problems {sum(bool(o['problems']) for o in out)}")
    print(f"wrote {path}  (fill human_label and failure_note for error analysis)")


if __name__ == "__main__":
    main()
