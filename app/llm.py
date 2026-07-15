"""OpenRouter client with JSON enforcement, one repair retry, and a demo-mode
fallback so a live demo can never dead-end on a missing key or provider outage."""

import json
import logging
import os
import re

import requests
from pydantic import ValidationError

from . import guardrails, prompts, samples
from .schemas import AnalysisResult, PolicyCitation, RetrievedChunk

log = logging.getLogger("compliance-copilot")

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "anthropic/claude-sonnet-4.5")
DEMO_MODEL_LABEL = "demo-mode (offline)"


def api_key() -> str:
    return os.getenv("OPENROUTER_API_KEY", "").strip()


def _extract_json(text: str) -> dict:
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.S)
    if fence:
        text = fence.group(1)
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object found in model output")
    return json.loads(text[start : end + 1])


def _chat(messages: list[dict], model: str) -> str:
    resp = requests.post(
        OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("APP_PUBLIC_URL", "http://localhost:8000"),
            "X-Title": "Compliance Copilot",
        },
        json={
            "model": model,
            "messages": messages,
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def analyze_with_llm(
    policy_type: str,
    chunks: list[RetrievedChunk],
    scenario_text: str,
    question: str,
    output_mode: str,
) -> tuple[AnalysisResult, str, bool]:
    """Returns (result, model_label, demo_mode)."""
    if not api_key():
        log.warning("OPENROUTER_API_KEY not set — serving demo-mode analysis")
        return _demo_analysis(chunks, scenario_text, question), DEMO_MODEL_LABEL, True

    model = DEFAULT_MODEL
    messages = [
        {"role": "system", "content": prompts.SYSTEM_PROMPT},
        {
            "role": "user",
            "content": prompts.build_user_prompt(policy_type, chunks, scenario_text, question, output_mode),
        },
    ]
    try:
        raw = _chat(messages, model)
        try:
            return AnalysisResult(**_extract_json(raw)), model, False
        except (ValueError, ValidationError, json.JSONDecodeError) as e:
            # One repair round-trip, then fall back
            messages += [
                {"role": "assistant", "content": raw},
                {"role": "user", "content": prompts.repair_prompt(raw, str(e))},
            ]
            raw2 = _chat(messages, model)
            return AnalysisResult(**_extract_json(raw2)), model, False
    except Exception as e:  # provider outage, bad key, unrepairable JSON
        log.error("LLM call failed (%s) — serving demo-mode analysis", e)
        return _demo_analysis(chunks, scenario_text, question), DEMO_MODEL_LABEL, True


def _demo_analysis(chunks: list[RetrievedChunk], scenario_text: str, question: str) -> AnalysisResult:
    """Offline fallback: exact canned result for known samples, otherwise a
    conservative 'Unclear' analysis grounded in the retrieved chunks."""
    for sample in samples.SAMPLES:
        if sample.scenario_text.strip() == scenario_text.strip():
            return samples.CANNED_RESULTS[sample.id]

    basis = [
        PolicyCitation(
            chunk_id=c.chunk_id,
            excerpt=(c.text[:140] + "…") if len(c.text) > 140 else c.text,
            point="Most relevant policy language retrieved for this scenario (offline heuristic match).",
        )
        for c in chunks[:3]
    ]
    return AnalysisResult(
        direct_answer=(
            "Offline demo mode: no AI provider is configured, so a full grounded "
            "analysis could not be generated. The most relevant policy clauses were "
            "retrieved below; route this scenario to a compliance officer for review."
        ),
        risk_level="Unclear",
        policy_basis=basis,
        missing_information=[
            "AI provider unavailable — full policy analysis not performed",
            "Compliance officer review of the retrieved clauses against the scenario",
        ],
        escalation_required=True,
        escalation_reason="Automated analysis unavailable; default to human review.",
        assumptions=["Retrieved clauses are the most relevant sections of the pasted policy."],
        internal_note=(
            f"Scenario received (question: {question[:160]}). Automated analysis "
            "unavailable; retrieved candidate policy clauses attached. Route to "
            "compliance review queue."
        ),
        customer_safe_response=(
            "Thank you for your query. It has been routed to our compliance team "
            "for review, and we will respond with next steps shortly."
        ),
        disclaimer=samples.DISCLAIMER,
    )


def run_analysis(
    policy_type: str,
    chunks: list[RetrievedChunk],
    scenario_text: str,
    question: str,
    output_mode: str,
) -> tuple[AnalysisResult, str, bool, bool]:
    """Full pipeline step: LLM (or fallback) + output guardrails.
    Returns (result, model_label, demo_mode, decision_language_scrubbed)."""
    result, model, demo = analyze_with_llm(policy_type, chunks, scenario_text, question, output_mode)
    result, scrubbed = guardrails.scrub_decision_language(result)
    return result, model, demo, scrubbed
