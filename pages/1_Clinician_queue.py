"""Clinician queue: review every alert before anything reaches a patient (human in the loop).

DEMO ONLY: in a real deployment this page needs clinician sign-in and role checks (RBAC).
"""
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_a.monitoring import ClinicianQueue, patient_summary  # noqa: E402


def show_summary(store, pid):
    """Side-by-side, read-only facts so the clinician can decide (no AI)."""
    s = patient_summary(store, pid)
    c = st.columns(4)
    with c[0]:
        st.markdown("**Latest labs**")
        for l in s["labs"]:
            prev = f" (was {l['previous']})" if "previous" in l else ""
            flag = f" :red[{l['flag']}]" if l["flag"] else ""
            st.caption(f"{l['test']} {l['value']} {l['unit']}{prev}{flag}")
        for sc in s["scores"]:
            prev = f" (was {sc['previous']})" if "previous" in sc else ""
            st.caption(f"{sc['score']} {sc['value']}{prev}")
    with c[1]:
        st.markdown("**Activity, 14 days**")
        w = s["watch"]
        if not w:
            st.caption("No watch data")
        elif not w.get("valid_days"):
            st.caption("Watch not worn recently")
        else:
            st.caption(f"{w['avg_steps']:,} steps a day")
            st.caption(f"{w['avg_active_min']} active min a day")
            if w.get("avg_sleep_hours"):
                st.caption(f"{w['avg_sleep_hours']} h sleep")
            st.caption(f"{w['valid_days']} days worn")
    with c[2]:
        st.markdown("**Weight, 60 days**")
        wt = s["weight"]
        if wt:
            sign = "+" if wt["change_kg"] > 0 else ""
            st.caption(f"{wt['latest_kg']} kg ({wt['latest_date']})")
            st.caption(f"{sign}{wt['change_kg']} kg since {wt['from_date']}")
        else:
            st.caption("No scale data")
    with c[3]:
        st.markdown("**Medicines**")
        for m in s["medications"] or ["None listed"]:
            st.caption(m)
    st.caption("Sources: labs, scores, watch data, home scale, medication list. Read-only.")


st.title("Clinician queue")
st.caption("Alerts from daily monitoring wait here. Nothing reaches the patient until you approve it.")

if "queue" not in st.session_state:
    st.session_state.queue = ClinicianQueue()
q = st.session_state.queue
clinician = st.sidebar.text_input("Reviewing clinician", value="Dr. Demo (fictional)")

if st.button("Run daily monitoring", icon=":material/monitor_heart:"):
    new = q.run_monitoring()
    st.success(f"{len(new)} new alert(s) waiting for review.")

colors = {"urgent": "red", "high": "orange", "medium": "blue", "low": "gray"}
pending = q.sorted_pending()
st.subheader(f"Waiting for review ({len(pending)})")
for p in pending:
    a = p["alert"]
    with st.container(border=True):
        st.markdown(f":{colors[a['priority']]}-badge[{a['priority'].upper()}] **{a['patient_id']}** · {a['rule_id']} · {a['trigger_date']}")
        st.write(f"Evidence: {a['detail']}")
        with st.expander("Patient summary", icon=":material/monitoring:"):
            show_summary(q.store, a["patient_id"])
        msg = st.text_area("Message to patient", value=p["draft_message"], key=f"msg-{a['key']}")
        note = st.text_input("Clinician note (audit log)", key=f"note-{a['key']}")
        c1, c2 = st.columns(2)
        if c1.button("Approve", key=f"ok-{a['key']}", type="primary"):
            q.decide(a["key"], "edit" if msg != p["draft_message"] else "approve", clinician, msg, note)
            st.rerun()
        if c2.button("Reject", key=f"no-{a['key']}"):
            q.decide(a["key"], "reject", clinician, note=note)
            st.rerun()

if q.done:
    st.subheader(f"Decided ({len(q.done)})")
    st.dataframe([{k: v for k, v in d.items() if k != "alert_key"} for d in q.done.values()], hide_index=True)
