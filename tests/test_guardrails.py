from app import guardrails
from app.samples import CANNED_RESULTS, DISCLAIMER
from app.schemas import AnalysisResult


def _result(**overrides) -> AnalysisResult:
    base = dict(
        direct_answer="The request needs review.",
        risk_level="Medium",
        policy_basis=[],
        missing_information=[],
        escalation_required=False,
        escalation_reason="",
        assumptions=[],
        internal_note="Note.",
        customer_safe_response="We will follow up.",
        disclaimer=DISCLAIMER,
    )
    base.update(overrides)
    return AnalysisResult(**base)


def test_detects_and_redacts_email_and_ssn():
    text = "Contact jane.doe@example.com, SSN 123-45-6789."
    found = guardrails.detect_pii(text)
    assert "email address" in found and "SSN-like identifier" in found
    redacted, labels = guardrails.redact_pii(text)
    assert "jane.doe@example.com" not in redacted
    assert "123-45-6789" not in redacted
    assert len(labels) >= 2


def test_clean_text_has_no_pii():
    assert guardrails.detect_pii("A distributor submitted incorporation documents.") == []


def test_decision_language_is_scrubbed():
    r = _result(direct_answer="The account is approved and you can proceed with onboarding.")
    scrubbed, changed = guardrails.scrub_decision_language(r)
    assert changed
    assert "is approved" not in scrubbed.direct_answer
    assert "human compliance review" in scrubbed.direct_answer


def test_advisory_language_untouched():
    r = _result(direct_answer="Escalation to compliance is recommended before proceeding.")
    scrubbed, changed = guardrails.scrub_decision_language(r)
    assert not changed
    assert scrubbed.direct_answer == r.direct_answer


def test_empty_disclaimer_backfilled():
    r = _result(disclaimer="   ")
    assert "human" in r.disclaimer.lower() or "compliance officer" in r.disclaimer.lower()


def test_all_canned_results_have_guardrail_fields():
    for rid, r in CANNED_RESULTS.items():
        assert r.disclaimer, rid
        assert r.policy_basis, rid
        assert r.missing_information, rid
        # canned demo answers never state a final decision
        _, changed = guardrails.scrub_decision_language(r)
        assert not changed, f"{rid} contains final-decision language"
