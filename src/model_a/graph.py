"""The same pipeline as a LangGraph graph (route, fixed reply or gather/generate/check,
retry once, then stop with the safe template). Requires `pip install langgraph`."""
from __future__ import annotations

from typing import Any, TypedDict

from .pipeline import (Answer, ModelA, needs_retry, step_check, step_finish, step_fixed, step_fallback,
                       step_gather, step_generate, step_route)


class TurnState(TypedDict, total=False):
    question: str
    session: Any
    store: Any
    pv: Any
    route: Any
    items: list
    answer: str
    attempts: int
    problems: list
    llm_used: bool
    escalation_id: str
    notes: list
    result: Any
    t0: float
    calls_start: int


def build_graph():
    from langgraph.graph import END, START, StateGraph

    g = StateGraph(TurnState)
    g.add_node("route", step_route)
    g.add_node("fixed_reply", step_fixed)
    g.add_node("gather", step_gather)
    g.add_node("generate", step_generate)
    g.add_node("check", step_check)
    g.add_node("fallback", step_fallback)
    g.add_node("finish", step_finish)
    g.add_edge(START, "route")
    g.add_conditional_edges("route", lambda s: "gather" if s["route"].kind == "answer" else "fixed_reply",
                            {"gather": "gather", "fixed_reply": "fixed_reply"})
    g.add_edge("fixed_reply", "finish")
    g.add_edge("gather", "generate")
    g.add_edge("generate", "check")
    g.add_conditional_edges("check", lambda s: "generate" if needs_retry(s) else "fallback",
                            {"generate": "generate", "fallback": "fallback"})
    g.add_edge("fallback", "finish")
    g.add_edge("finish", END)
    return g.compile()


class GraphModelA(ModelA):
    """ModelA that runs each turn through the compiled LangGraph."""

    def __init__(self, store=None):
        super().__init__(store)
        self.graph = build_graph()

    def ask(self, session, question: str) -> Answer:
        import time
        from . import llm
        out = self.graph.invoke({"question": question, "session": session, "store": self.store,
                                 "pv": self.store.for_patient(session.patient_id), "t0": time.perf_counter(),
                                 "calls_start": len(llm.CALLS)})
        return out["result"]
