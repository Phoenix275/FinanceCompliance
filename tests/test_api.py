from fastapi.testclient import TestClient

from app.main import app
from app.samples import SAMPLES

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_samples_listed():
    r = client.get("/api/samples")
    assert r.status_code == 200
    assert len(r.json()["samples"]) >= 3  # PRD: at least three synthetic scenarios


def test_empty_inputs_rejected_with_friendly_message():
    r = client.post("/api/analyze", json={"policy_text": "", "scenario_text": "x", "question": "y"})
    assert r.status_code == 422
    assert "policy" in r.json()["detail"].lower()


def test_analyze_sample_end_to_end_demo_mode(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    s = SAMPLES[0]
    r = client.post("/api/analyze", json={
        "policy_type": s.policy_type,
        "policy_text": s.policy_text,
        "scenario_text": s.scenario_text,
        "question": s.question,
    })
    assert r.status_code == 200
    data = r.json()
    assert data["demo_mode"] is True
    res = data["result"]
    # PRD acceptance criteria: all output sections present
    for field in ("direct_answer", "policy_basis", "risk_level", "missing_information",
                  "escalation_required", "internal_note", "disclaimer"):
        assert field in res
    assert res["risk_level"] in ("Low", "Medium", "High", "Unclear")
    assert data["retrieved_chunks"]
    assert data["guardrails"]["grounded_chunks"] > 0


def test_pii_is_detected_and_redacted(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    r = client.post("/api/analyze", json={
        "policy_text": "1. Vendors must be screened.\n2. Payments require approval.\n3. Report issues.",
        "scenario_text": "Vendor contact is jane.doe@example.com and card 4111 1111 1111 1111.",
        "question": "Can we pay this vendor?",
    })
    assert r.status_code == 200
    g = r.json()["guardrails"]
    assert g["pii_detected"] and g["pii_redacted"]


def test_export_markdown(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    s = SAMPLES[1]
    analysis = client.post("/api/analyze", json={
        "policy_type": s.policy_type, "policy_text": s.policy_text,
        "scenario_text": s.scenario_text, "question": s.question,
    }).json()
    r = client.post("/api/export", json={"result": analysis["result"], "meta": {"policy_type": s.policy_type}})
    assert r.status_code == 200
    md = r.text
    assert md.startswith("# Compliance Analysis Memo")
    assert "## Policy basis" in md and "## Customer-safe response" in md


def test_audit_trail_populated():
    r = client.get("/api/audit")
    assert r.status_code == 200
    assert len(r.json()["entries"]) >= 1
