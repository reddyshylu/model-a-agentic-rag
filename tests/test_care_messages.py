"""Approved messages reach only the right patient; rejected ones never do."""
import json

from model_a import config, monitoring
from model_a.records import RecordStore


def test_patient_messages_scoped_and_approved_only(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ESCALATIONS", tmp_path)
    rows = [
        {"time": "2026-11-05T10:00:00", "patient_id": "P01", "action": "approve", "patient_message": "A for P01", "rule_id": "R07"},
        {"time": "2026-11-05T11:00:00", "patient_id": "P01", "action": "reject", "patient_message": None, "rule_id": "R01"},
        {"time": "2026-11-05T12:00:00", "patient_id": "P02", "action": "approve", "patient_message": "B for P02", "rule_id": "R07"},
        {"time": "2026-11-05T13:00:00", "patient_id": "P01", "action": "edit", "patient_message": "C edited", "rule_id": "R10"},
    ]
    (tmp_path / "clinician_audit.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\nnot json\n", encoding="utf-8")
    msgs = monitoring.patient_messages("P01")
    assert [m["message"] for m in msgs] == ["C edited", "A for P01"]
    assert monitoring.patient_messages("P99") == []


def test_messages_flow_after_clinician_decision(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "ESCALATIONS", tmp_path)
    q = monitoring.ClinicianQueue()
    q.run_monitoring()
    first, second = q.sorted_pending()[:2]
    assert monitoring.patient_messages(first["alert"]["patient_id"]) == []  # pending: nothing yet
    q.decide(first["alert"]["key"], "approve", "Dr. Test")
    q.decide(second["alert"]["key"], "reject", "Dr. Test")
    assert len(monitoring.patient_messages(first["alert"]["patient_id"])) >= 1
    if second["alert"]["patient_id"] != first["alert"]["patient_id"]:
        assert monitoring.patient_messages(second["alert"]["patient_id"]) == []


def test_patient_summary_is_scoped():
    s = monitoring.patient_summary(RecordStore(), "P08")
    assert s["watch"]["avg_steps"] < 2000
    assert {l["source"].split()[0] for l in s["labs"]} == {"labs"}
    assert all(isinstance(m, str) for m in s["medications"])
