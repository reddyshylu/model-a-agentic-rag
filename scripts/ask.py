"""Chat with Model A as one fictional patient.

    python scripts/ask.py --patient P13
    python scripts/ask.py --patient P13 "my AST is 81 is that bad??"
Add --graph to run each turn through LangGraph (needs `pip install langgraph`).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a.pipeline import ModelA  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--patient", required=True, help="Fictional patient id, P01 to P30")
    ap.add_argument("--graph", action="store_true")
    ap.add_argument("question", nargs="*")
    a = ap.parse_args()
    if a.graph:
        from model_a.graph import GraphModelA
        model = GraphModelA()
    else:
        model = ModelA()
    session = model.start_session(a.patient)
    questions = [" ".join(a.question)] if a.question else None
    while True:
        q = questions.pop(0) if questions else input("\nYou: ").strip()
        if not q or q.lower() in ("quit", "exit"):
            break
        ans = model.ask(session, q)
        print(f"\nModel A [{ans.route}]: {ans.text}")
        if ans.escalation_id:
            print(f"(care team alerted: {ans.escalation_id})")
        if questions is not None and not questions:
            break


if __name__ == "__main__":
    main()
