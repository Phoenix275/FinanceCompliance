"""Compliance Copilot — FastAPI app.

Serves the single-page UI plus a small JSON API:
  GET  /api/health   — key/model status for the header badge
  GET  /api/samples  — synthetic scenario library
  POST /api/analyze  — retrieval + LLM + guardrails pipeline
  GET  /api/audit    — in-memory audit trail (no data persistence)
  POST /api/export   — render a result as a Markdown memo
"""

import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from . import guardrails, llm, prompts, retrieval, samples
from .schemas import AnalyzeRequest, AnalyzeResponse, AuditEntry, GuardrailReport

load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Compliance Copilot", version="1.0.0")

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

# In-memory only, per PRD: no persistence of user inputs.
AUDIT_LOG: list[AuditEntry] = []
MAX_AUDIT = 50


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ai_configured": bool(llm.api_key()),
        "model": llm.DEFAULT_MODEL if llm.api_key() else llm.DEMO_MODEL_LABEL,
    }


@app.get("/api/samples")
def get_samples():
    return {"samples": [s.model_dump() for s in samples.SAMPLES]}


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not req.policy_text.strip():
        raise HTTPException(422, "Please provide the source policy text — the analysis is grounded only in it.")
    if not req.scenario_text.strip():
        raise HTTPException(422, "Please describe the scenario (synthetic data only).")
    if not req.question.strip():
        raise HTTPException(422, "Please enter the compliance question to analyze.")

    started = time.time()

    # Guardrail 1: PII scan/redaction on inputs (synthetic-data policy)
    combined_pii = sorted(set(guardrails.detect_pii(req.policy_text)
                              + guardrails.detect_pii(req.scenario_text)
                              + guardrails.detect_pii(req.question)))
    scenario_text, question, policy_text = req.scenario_text, req.question, req.policy_text
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
    AUDIT_LOG.append(entry)
    del AUDIT_LOG[:-MAX_AUDIT]

    return AnalyzeResponse(
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


@app.get("/api/audit")
def audit():
    return {"entries": [e.model_dump() for e in reversed(AUDIT_LOG)]}


@app.post("/api/export", response_class=PlainTextResponse)
def export_markdown(payload: dict):
    try:
        return prompts.to_markdown(payload["result"], payload.get("meta", {}))
    except (KeyError, TypeError) as e:
        raise HTTPException(422, f"Invalid export payload: {e}")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
