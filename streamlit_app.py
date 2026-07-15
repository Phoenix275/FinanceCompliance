"""Compliance Copilot — Streamlit entrypoint for Streamlit Community Cloud.

Runs the exact same engine as the FastAPI app (app/pipeline.py): clause-level
retrieval with cited chunks, PII redaction, decision-language scrubbing, an
LLM fallback chain, and offline demo mode. Deploy: share.streamlit.io → this
repo → main file `streamlit_app.py`; put OPENROUTER_API_KEY in app secrets.
"""

import os

import streamlit as st

# Secrets → env before the engine reads them (Community Cloud uses st.secrets)
try:
    for k in ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "OPENROUTER_MAX_TOKENS"):
        if k in st.secrets:
            os.environ.setdefault(k, str(st.secrets[k]))
except FileNotFoundError:
    pass

from dotenv import load_dotenv

load_dotenv()

from app import llm, pdf_export, pipeline, prompts, samples  # noqa: E402
from app.schemas import AnalyzeRequest  # noqa: E402

st.set_page_config(page_title="Compliance Copilot", page_icon="🛡️", layout="wide")

ACCENT = "#5b2d90"
RISK_STYLE = {
    "Low": ("#0f7b4d", "#e2f5ec"),
    "Medium": ("#a05a00", "#fdf0dd"),
    "High": ("#b3261e", "#fde7e5"),
    "Unclear": ("#4a5568", "#eceff4"),
}

st.markdown(f"""
<style>
  .block-container {{ padding-top: 1.4rem; }}
  .cc-header {{ background: linear-gradient(120deg,#3b1d63,{ACCENT} 55%,#7b4bb3);
    color:#fff; border-radius:14px; padding:18px 24px; margin-bottom:6px; }}
  .cc-header h1 {{ margin:0; font-size:24px; color:#fff; }}
  .cc-header p {{ margin:4px 0 0; opacity:.85; font-size:14px; }}
  .cc-badge {{ display:inline-block; font-size:12px; padding:3px 12px; border-radius:999px;
    margin-top:8px; margin-right:6px; border:1px solid rgba(255,255,255,.35);
    background:rgba(255,255,255,.14); color:#fff; }}
  .cc-banner {{ background:#fff8e6; border:1px solid #f1e3b8; color:#6b5410;
    border-radius:10px; padding:8px 14px; font-size:13px; margin:10px 0 4px; }}
  .risk-pill {{ font-weight:800; padding:6px 16px; border-radius:999px; font-size:14px;
    display:inline-block; margin-right:8px; }}
  .gchip {{ display:inline-block; font-size:12px; padding:3px 10px; border-radius:999px;
    background:#f0e9fa; color:{ACCENT}; font-weight:600; margin:2px 4px 2px 0; }}
  .gchip.warn {{ background:#fdf0dd; color:#a05a00; }}
  .cite {{ border:1px solid #e3e6ef; border-left:4px solid {ACCENT}; border-radius:8px;
    padding:10px 13px; margin:8px 0; background:#fbfaff; }}
  .cite .q {{ font-style:italic; color:#3c3560; }}
  .cite .p {{ font-size:13px; color:#5b6274; margin-top:4px; }}
  .cite .id {{ font-size:11px; font-weight:800; color:{ACCENT}; letter-spacing:.4px; }}
  .disclaimer {{ background:#eceff4; border-radius:8px; padding:10px 14px;
    font-size:12.5px; color:#4a5568; margin-top:10px; }}
</style>""", unsafe_allow_html=True)

ai_live = bool(llm.api_key())
mode_badge = (f"● Live AI · {llm.DEFAULT_MODEL}" if ai_live
              else "● Demo mode (no API key) — canned analyses")

st.markdown(f"""
<div class="cc-header">
  <h1>🛡️ Compliance Copilot</h1>
  <p>Policy-grounded RAG assistant for finance &amp; compliance teams · third-party due diligence · HCP interactions · trade compliance · expense controls</p>
  <span class="cc-badge">{mode_badge}</span><span class="cc-badge">Human-in-the-loop by design</span>
</div>
<div class="cc-banner">🧪 <b>Synthetic data only</b> — do not paste real customer, employee, patient, vendor, or regulated data. Inputs are scanned and PII is auto-redacted.</div>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.subheader("Sample scenario library")
    st.caption("All scenarios are synthetic (fictional entities, people, and numbers).")
    titles = ["— Start blank —"] + [s.title for s in samples.SAMPLES]
    picked = st.selectbox("Load a scenario", titles, label_visibility="collapsed")
    sample = next((s for s in samples.SAMPLES if s.title == picked), None)

    policy_type = st.selectbox("Policy type", [
        "Third-party / anti-bribery", "HCP interactions", "Gifts & hospitality",
        "Trade compliance / sanctions", "Anti-bribery / finance controls",
        "KYC / AML", "Internal policy",
    ], index=0 if sample is None else max(0, [
        "Third-party / anti-bribery", "HCP interactions", "Gifts & hospitality",
        "Trade compliance / sanctions", "Anti-bribery / finance controls",
        "KYC / AML", "Internal policy",
    ].index(sample.policy_type)))

    output_mode = st.radio("Answer for", ["Compliance Analyst", "Operations", "Executive Summary"])
    redact = st.toggle("Auto-redact detected PII", value=True)
    st.divider()
    st.caption("⚖️ Assistive analysis only — final decisions rest with human compliance officers. "
               "No data is persisted.")

# ----------------------------------------------------------------- inputs
left, right = st.columns([5, 7], gap="large")

with left:
    st.subheader("1 · Describe the case")
    with st.form("analysis_form"):
        policy_text = st.text_area("Source policy text (the only source of truth)",
                                   value=sample.policy_text if sample else "", height=230)
        scenario_text = st.text_area("Scenario details (synthetic)",
                                     value=sample.scenario_text if sample else "", height=140)
        question = st.text_area("Compliance question",
                                value=sample.question if sample else "", height=70)
        submitted = st.form_submit_button("🛡️ Analyze compliance risk", type="primary",
                                          width='stretch')

if submitted:
    if not (policy_text.strip() and scenario_text.strip() and question.strip()):
        st.error("Please provide the policy text, scenario, and question — the analysis is grounded only in what you supply.")
    else:
        with st.spinner("Retrieving policy clauses and generating grounded analysis…"):
            response, entry = pipeline.analyze_case(AnalyzeRequest(
                policy_type=policy_type, policy_text=policy_text,
                scenario_text=scenario_text, question=question,
                output_mode=output_mode, redact_pii=redact,
            ))
        st.session_state["last"] = response
        st.session_state.setdefault("audit", []).append(entry)

# ----------------------------------------------------------------- results
with right:
    st.subheader("2 · Grounded analysis")
    data = st.session_state.get("last")
    if not data:
        st.info("Risk level, cited policy basis, missing-information checklist, escalation "
                "recommendation, internal note, and a customer-safe response — every claim "
                "traceable to a policy clause.")
    else:
        r = data.result
        fg, bg = RISK_STYLE[r.risk_level]
        esc_txt = "🚩 Escalation required" if r.escalation_required else "✓ No escalation needed"
        esc_fg, esc_bg = (RISK_STYLE["High"] if r.escalation_required else RISK_STYLE["Low"])
        st.markdown(
            f'<span class="risk-pill" style="color:{fg};background:{bg}">RISK: {r.risk_level.upper()}</span>'
            f'<span class="risk-pill" style="color:{esc_fg};background:{esc_bg};font-size:12.5px">{esc_txt}</span>'
            f'<span style="color:#5b6274;font-size:12px"> {data.model} · {data.latency_ms} ms</span>',
            unsafe_allow_html=True)
        st.markdown(f"**{r.direct_answer}**")

        g = data.guardrails
        chips = [f'<span class="gchip">📖 Grounded in {g.grounded_chunks} policy chunks</span>']
        chips.append(f'<span class="gchip warn">🔒 PII detected: {", ".join(g.pii_detected)}'
                     f'{" — redacted" if g.pii_redacted else ""}</span>'
                     if g.pii_detected else '<span class="gchip">🔒 No PII detected</span>')
        if g.decision_language_scrubbed:
            chips.append('<span class="gchip warn">🛡 Decision language rephrased to advisory</span>')
        chips.append('<span class="gchip">👤 Human review required</span>')
        if data.demo_mode:
            chips.append('<span class="gchip warn">⚠ Offline demo response</span>')
        st.markdown("".join(chips), unsafe_allow_html=True)

        with st.expander(f"📖 Policy basis — cited evidence ({len(r.policy_basis)})", expanded=True):
            for c in r.policy_basis:
                st.markdown(f'<div class="cite"><span class="id">CHUNK {c.chunk_id}</span>'
                            f'<div class="q">“{c.excerpt}”</div>'
                            f'<div class="p">{c.point}</div></div>', unsafe_allow_html=True)

        with st.expander(f"🔎 Retrieved policy chunks — what the AI was allowed to see ({len(data.retrieved_chunks)})"):
            for c in data.retrieved_chunks:
                st.markdown(f"**Chunk {c.chunk_id}** (relevance {c.score:.2f}) — {c.text}")

        with st.expander(f"📋 Missing information checklist ({len(r.missing_information)})", expanded=True):
            for m in r.missing_information or ["None identified"]:
                st.checkbox(m, key=f"miss-{hash(m)}")

        if r.escalation_required:
            st.warning(f"**Escalation:** {r.escalation_reason}")

        with st.expander(f"💭 Assumptions ({len(r.assumptions)})"):
            for a in r.assumptions or ["None"]:
                st.markdown(f"- {a}")

        with st.expander("🗒️ Internal note (CRM / ticket draft)", expanded=False):
            st.code(r.internal_note, language=None, wrap_lines=True)
        with st.expander("✉️ Customer-safe response", expanded=False):
            st.code(r.customer_safe_response, language=None, wrap_lines=True)

        st.markdown(f'<div class="disclaimer">⚖️ {r.disclaimer}</div>', unsafe_allow_html=True)

        meta = {"policy_type": policy_type, "model": data.model}
        d1, d2 = st.columns(2)
        d1.download_button("⬇ Download PDF memo",
                           pdf_export.build_pdf(r.model_dump(), meta),
                           "compliance-analysis-memo.pdf", "application/pdf",
                           width='stretch')
        d2.download_button("⬇ Download Markdown memo",
                           prompts.to_markdown(r.model_dump(), meta),
                           "compliance-analysis-memo.md", "text/markdown",
                           width='stretch')

    audit = st.session_state.get("audit", [])
    if audit:
        with st.expander(f"🧾 Audit trail — session, in-memory only ({len(audit)})"):
            st.dataframe(
                [{"Time (UTC)": e.timestamp.replace("T", " ").replace("+00:00", ""),
                  "Policy type": e.policy_type, "Question": e.question,
                  "Risk": e.risk_level, "Escalate": "🚩" if e.escalation_required else "—",
                  "PII": "🔒" if e.pii_detected else "—", "Model": e.model}
                 for e in reversed(audit)],
                width='stretch', hide_index=True)
