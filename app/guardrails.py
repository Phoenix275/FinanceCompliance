"""Responsible-AI guardrails.

1. PII detection/redaction on inputs (synthetic-data policy enforcement).
2. Decision-language scrubbing on outputs — the assistant must never sound
   like it made a final compliance decision.
3. Disclaimer enforcement (also backstopped by the pydantic validator).
"""

import re

from .schemas import AnalysisResult

PII_PATTERNS: dict[str, re.Pattern] = {
    "email address": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone number": re.compile(r"(?<!\d)(?:\+?\d{1,3}[\s-]?)?(?:\(\d{3}\)|\d{3})[\s-]?\d{3}[\s-]?\d{4}(?!\d)"),
    "SSN-like identifier": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "card/account number": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "PAN-like identifier": re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),
    "IBAN-like identifier": re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b"),
}

REDACTION = "[REDACTED-{label}]"


def detect_pii(text: str) -> list[str]:
    return [label for label, pattern in PII_PATTERNS.items() if pattern.search(text)]


def redact_pii(text: str) -> tuple[str, list[str]]:
    found: list[str] = []
    for label, pattern in PII_PATTERNS.items():
        if pattern.search(text):
            found.append(label)
            text = pattern.sub(REDACTION.format(label=label.split()[0].upper()), text)
    return text, found


# Phrases that read as a final decision rather than a recommendation.
_DECISION_PHRASES = [
    (re.compile(r"\b(is|are|has been|have been)\s+(hereby\s+)?approved\b", re.I),
     "is recommended for approval pending human compliance review"),
    (re.compile(r"\b(is|are|has been|have been)\s+(hereby\s+)?rejected\b", re.I),
     "is recommended for rejection pending human compliance review"),
    (re.compile(r"\byou (can|may) (now )?(proceed|activate|onboard|release)\b", re.I),
     "proceeding appears consistent with policy, subject to human compliance review"),
    (re.compile(r"\baccount (is|has been) activated\b", re.I),
     "account activation appears policy-consistent, subject to human compliance review"),
    (re.compile(r"\btransaction (is|has been) (cleared|blocked)\b", re.I),
     "a transaction hold/clearance decision should be made by the compliance officer"),
]


def scrub_decision_language(result: AnalysisResult) -> tuple[AnalysisResult, bool]:
    """Rewrite final-decision phrasing in user-facing fields; report if anything changed."""
    changed = False
    data = result.model_dump()
    for field in ("direct_answer", "internal_note", "customer_safe_response"):
        text = data[field]
        for pattern, replacement in _DECISION_PHRASES:
            new_text = pattern.sub(replacement, text)
            if new_text != text:
                changed = True
                text = new_text
        data[field] = text
    return AnalysisResult(**data), changed
