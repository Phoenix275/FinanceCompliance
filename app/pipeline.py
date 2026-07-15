"""Framework-agnostic analysis pipeline — shared by the FastAPI API and the
Streamlit app so both UIs run the identical engine."""

import time
from datetime import datetime, timezone

from . import guardrails, llm, retrieval
from .schemas import AnalyzeRequest, AnalyzeResponse, AuditEntry, GuardrailReport


def analyze_case(req: AnalyzeRequest) -> tuple[AnalyzeResponse, AuditEntry]:
    started = time.time()

    # Guardrail 1: PII scan/redaction on inputs (synthetic-data policy)
    combined_pii = sorted(set(guardrails.detect_pii(req.policy_text)
                              + guardrails.detect_pii(req.scenario_text)
                              + guardrails.detect_pii(req.question)))
    policy_text, scenario_text, question = req.policy_text, req.scenario_text, req.question
    redacted = False
    if combined_pii and req.redact_pii:
        policy_text, _ = guardrails.redact_pii(policy_text)
        scenario_text, _ = guardrails.redact_pii(scenario_text)
        question, _ = guardrails.redact_pii(question)
        redacted = True

    # RAG: retrieve only the relevant policy clauses
    chunks = retrieval.retrieve(policy_text, scenario_text, question)

    # LLM + output guardrails (falls back to demo mode if provider unavailable)
    result, model, demo, scrubbed = llm.run_analysis(
        req.policy_type, chunks, scenario_text, question, req.output_mode
    )

    response = AnalyzeResponse(
        result=result,
        retrieved_chunks=chunks,
        guardrails=GuardrailReport(
            pii_detected=combined_pii,
            pii_redacted=redacted,
            decision_language_scrubbed=scrubbed,
            grounded_chunks=len(chunks),
        ),
        model=model,
        demo_mode=demo,
        latency_ms=int((time.time() - started) * 1000),
    )
    entry = AuditEntry(
        timestamp=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        policy_type=req.policy_type,
        question=req.question[:120],
        risk_level=result.risk_level,
        escalation_required=result.escalation_required,
        model=model,
        demo_mode=demo,
        pii_detected=bool(combined_pii),
    )
    return response, entry
