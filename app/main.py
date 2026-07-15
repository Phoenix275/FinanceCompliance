"""Compliance Copilot — FastAPI app.

Serves the single-page UI plus a small JSON API:
  GET  /api/health   — key/model status for the header badge
  GET  /api/samples  — synthetic scenario library
  POST /api/analyze  — retrieval + LLM + guardrails pipeline
  GET  /api/audit    — in-memory audit trail (no data persistence)
  POST /api/export   — render a result as a Markdown memo
"""

import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles

from . import llm, pdf_export, pipeline, prompts, samples
from .schemas import AnalyzeRequest, AnalyzeResponse, AuditEntry

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

    response, entry = pipeline.analyze_case(req)
    AUDIT_LOG.append(entry)
    del AUDIT_LOG[:-MAX_AUDIT]
    return response


@app.get("/api/audit")
def audit():
    return {"entries": [e.model_dump() for e in reversed(AUDIT_LOG)]}


@app.post("/api/export", response_class=PlainTextResponse)
def export_markdown(payload: dict):
    try:
        return prompts.to_markdown(payload["result"], payload.get("meta", {}))
    except (KeyError, TypeError) as e:
        raise HTTPException(422, f"Invalid export payload: {e}")


@app.post("/api/export/pdf")
def export_pdf(payload: dict):
    try:
        content = pdf_export.build_pdf(payload["result"], payload.get("meta", {}))
    except (KeyError, TypeError) as e:
        raise HTTPException(422, f"Invalid export payload: {e}")
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="compliance-analysis-memo.pdf"'},
    )


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
