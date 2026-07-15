# Compliance Copilot — Policy-Grounded RAG Assistant

A finance & compliance RAG assistant built for the **GE HealthCare enterprise AI workshop**. Compliance, risk, audit, and operations teams paste a policy, describe a (synthetic) scenario, and ask a question — the assistant returns a structured, **policy-cited** analysis: risk level, evidence, missing-information checklist, escalation recommendation, an internal CRM note, and a customer-safe response.

**Stack:** Python 3.10+ · FastAPI · vanilla JS single-page UI · OpenRouter (any model) · zero database.

## Why this scores

| Judging criterion | Weight | Where it shows in this app |
|---|---|---|
| Working deployed app | 30% | Single FastAPI service (UI + API), Dockerfile, `render.yaml` one-click blueprint, **demo mode** fallback so the live demo never dead-ends on a key/provider failure |
| Clear enterprise workflow | 20% | Header states the problem in one line; 5 realistic GE HealthCare compliance scenarios (distributor due diligence, HCP payments, gifts & hospitality, sanctions screening, tender red flags); role-based output modes (Analyst / Operations / Executive) |
| Quality of AI output | 25% | Real lightweight RAG: policy is chunked, TF-IDF-retrieved, and **every policy_basis item cites a chunk ID with a verbatim quote**; strict JSON contract with pydantic validation and one automatic repair retry |
| Responsible AI guardrails | 10% | PII auto-detection & redaction on inputs, decision-language scrubber on outputs ("is approved" → "recommended pending human review"), enforced disclaimer, visible guardrail chips, in-memory audit trail |
| UX clarity | 10% | Sample loader, risk badge + escalation flag header, collapsible evidence sections, copy buttons, Markdown memo download |
| Synthetic data use | 5% | All scenarios synthetic; persistent banner; PII scanner enforces the policy technically, not just verbally |

## Run locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # add your OPENROUTER_API_KEY (optional — demo mode works without it)
uvicorn app.main:app --reload
# open http://localhost:8000
```

Run the test suite (17 tests covering guardrails, retrieval, and the API contract):

```bash
python -m pytest tests/ -q
```

## Deploy (pick one)

- **Render (fastest):** push to GitHub → render.com → New → Blueprint → select repo. `render.yaml` does the rest; set `OPENROUTER_API_KEY` in the dashboard.
- **Docker anywhere (AWS/Azure/VPS):** `docker build -t compliance-copilot . && docker run -p 8000:8000 -e OPENROUTER_API_KEY=sk-or-... compliance-copilot`
- **AWS App Runner / Azure Container Apps:** point at the Dockerfile; put the key in Secrets Manager / Key Vault.

## Architecture

```
Browser (static/index.html)
   │  POST /api/analyze
   ▼
FastAPI (app/main.py)
   ├─ guardrails.py   PII scan + redact (input) · decision-language scrub (output)
   ├─ retrieval.py    clause-level chunking + TF-IDF top-k retrieval  ← the "RAG"
   ├─ prompts.py      system contract: grounded-only, no final decisions, cite chunk IDs
   ├─ llm.py          OpenRouter JSON call → pydantic validate → 1 repair retry
   │                  └─ falls back to demo-mode canned/heuristic result on any failure
   └─ samples.py      5 synthetic GE HealthCare compliance scenarios + canned results
```

No data persistence: inputs live only in the request; the audit trail is in-memory and capped.

## Demo script (3 minutes)

1. **Problem (20s):** point at the header — compliance teams answer the same policy questions inconsistently; this grounds every answer in the policy itself.
2. **Load** "Third-party distributor onboarding" from the sample library — note the synthetic-data banner and that the policy text is the only source of truth.
3. **Analyze:** show the **High risk** badge, escalation flag, and the **cited policy basis** — open "Retrieved policy chunks" to show exactly what the model was allowed to see.
4. **Guardrails:** point at the chips (grounded chunks, PII scan, human-review). Paste an email address into the scenario and re-run — watch it get detected and redacted.
5. **Workflow value:** open the internal note (copy → CRM) and the customer-safe response (no internal risk logic leaked). Download the Markdown memo.
6. **Close:** flip output mode to Executive, re-run, and show the audit trail. "Assistive, cited, human-in-the-loop — and deployable anywhere with one Docker image."

## Guardrails in depth

- The model is instructed it **cannot** approve/reject/onboard/block anything; a regex scrubber additionally rewrites any decision-sounding output to advisory language and flags that it did so.
- `risk_level: "Unclear"` is a first-class outcome when policy or facts are insufficient.
- The customer-safe response is prompt-separated from internal reasoning and never exposes risk ratings or screening results.
- Disclaimer is triple-enforced: prompt contract → pydantic validator backfill → always rendered in the UI.

*All names, policies, entities, and numbers in the samples are fictional. This tool assists analysis; final decisions rest with human compliance officers.*
