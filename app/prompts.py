"""Prompt contract — the AI's rules of engagement, per PRD section 9."""

from .schemas import RetrievedChunk

SYSTEM_PROMPT = """You are a policy-grounded compliance analysis assistant for a healthcare technology enterprise's finance, compliance, risk, and audit teams.

STRICT RULES:
1. Use ONLY the provided policy excerpts as the source of truth. Never invent policy requirements or cite regulations not present in the excerpts.
2. NEVER make or imply a final decision. You do not approve, reject, onboard, activate, block, clear, or release anything. You analyze and recommend; a human compliance officer decides.
3. Cite evidence: every policy_basis item must reference the chunk_id of a provided excerpt and include a short verbatim quote from it.
4. Clearly separate policy facts (policy_basis) from assumptions (assumptions) and unknowns (missing_information).
5. If the policy language is insufficient or scenario facts are incomplete for a confident assessment, set risk_level to "Unclear" and enumerate what is missing.
6. The customer_safe_response must be professional and must NOT reveal internal risk logic, risk ratings, screening results, or escalation details.
7. Always include the human-review disclaimer.
8. All data is synthetic demo data; still treat it with professional care.

OUTPUT: Respond with ONLY a single JSON object, no markdown fences, matching exactly this schema:
{
  "direct_answer": "string — direct answer to the question, grounded in policy",
  "risk_level": "Low | Medium | High | Unclear",
  "policy_basis": [{"chunk_id": 1, "excerpt": "verbatim quote from that chunk", "point": "how it applies"}],
  "missing_information": ["string"],
  "escalation_required": true,
  "escalation_reason": "string (empty string if no escalation needed)",
  "assumptions": ["string"],
  "internal_note": "string — CRM/compliance ticket note for internal use",
  "customer_safe_response": "string — external-safe wording",
  "disclaimer": "string — human compliance review disclaimer"
}"""

_MODE_GUIDANCE = {
    "Compliance Analyst": "Write for a compliance analyst: precise policy language, clause-level reasoning.",
    "Operations": "Write for an operations agent: plain language, focus on proceed/hold/escalate and exactly what to collect next.",
    "Executive Summary": "Write for an executive: lead with the bottom line and business exposure in the direct_answer; keep everything tight.",
}


def build_user_prompt(
    policy_type: str,
    chunks: list[RetrievedChunk],
    scenario_text: str,
    question: str,
    output_mode: str,
) -> str:
    excerpts = "\n\n".join(f"[Chunk {c.chunk_id}] {c.text}" for c in chunks)
    return f"""POLICY TYPE: {policy_type}

RETRIEVED POLICY EXCERPTS (your ONLY source of truth — cite by chunk_id):
{excerpts}

SCENARIO (synthetic):
{scenario_text}

COMPLIANCE QUESTION:
{question}

AUDIENCE: {_MODE_GUIDANCE.get(output_mode, _MODE_GUIDANCE['Compliance Analyst'])}

Return the JSON object now."""


def repair_prompt(bad_output: str, error: str) -> str:
    return (
        "Your previous response could not be parsed as valid JSON matching the schema. "
        f"Parse error: {error}\n\nPrevious response:\n{bad_output[:2000]}\n\n"
        "Return ONLY the corrected single JSON object, no commentary, no markdown fences."
    )


def to_markdown(result: dict, meta: dict) -> str:
    """Render an analysis as a downloadable Markdown memo."""
    lines = [
        "# Compliance Analysis Memo",
        "",
        f"- **Policy type:** {meta.get('policy_type', '')}",
        f"- **Risk level:** {result['risk_level']}",
        f"- **Escalation required:** {'Yes' if result['escalation_required'] else 'No'}",
        f"- **Model:** {meta.get('model', '')}",
        "",
        "## Direct answer",
        result["direct_answer"],
        "",
        "## Policy basis",
    ]
    for c in result["policy_basis"]:
        lines.append(f"- **[Chunk {c['chunk_id']}]** \"{c['excerpt']}\" — {c['point']}")
    lines += ["", "## Missing information"]
    lines += [f"- [ ] {m}" for m in result["missing_information"]] or ["- None identified"]
    if result["escalation_required"]:
        lines += ["", "## Escalation", result["escalation_reason"]]
    lines += ["", "## Assumptions"]
    lines += [f"- {a}" for a in result["assumptions"]] or ["- None"]
    lines += [
        "", "## Internal note", result["internal_note"],
        "", "## Customer-safe response", result["customer_safe_response"],
        "", "---", f"> {result['disclaimer']}",
    ]
    return "\n".join(lines)
