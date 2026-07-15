"""Pydantic models — the strict response contract the LLM must satisfy."""

from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class PolicyCitation(BaseModel):
    chunk_id: int = Field(description="ID of the retrieved policy chunk this point is grounded in")
    excerpt: str = Field(description="Short verbatim quote from the policy chunk")
    point: str = Field(description="How this policy language applies to the scenario")


class AnalysisResult(BaseModel):
    direct_answer: str
    risk_level: Literal["Low", "Medium", "High", "Unclear"]
    policy_basis: list[PolicyCitation]
    missing_information: list[str]
    escalation_required: bool
    escalation_reason: str
    assumptions: list[str]
    internal_note: str
    customer_safe_response: str
    disclaimer: str

    @field_validator("disclaimer")
    @classmethod
    def disclaimer_not_empty(cls, v: str) -> str:
        if not v.strip():
            return (
                "This is an AI-assisted analysis for internal triage only. "
                "It is not a final compliance decision. A qualified compliance "
                "officer must review before any action is taken."
            )
        return v


class RetrievedChunk(BaseModel):
    chunk_id: int
    text: str
    score: float


class AnalyzeRequest(BaseModel):
    policy_type: str = "Internal policy"
    policy_text: str
    scenario_text: str
    question: str
    output_mode: Literal["Compliance Analyst", "Operations", "Executive Summary"] = "Compliance Analyst"
    redact_pii: bool = True


class GuardrailReport(BaseModel):
    pii_detected: list[str] = []
    pii_redacted: bool = False
    decision_language_scrubbed: bool = False
    grounded_chunks: int = 0


class AnalyzeResponse(BaseModel):
    result: AnalysisResult
    retrieved_chunks: list[RetrievedChunk]
    guardrails: GuardrailReport
    model: str
    demo_mode: bool = False
    latency_ms: int = 0


class Sample(BaseModel):
    id: str
    title: str
    policy_type: str
    policy_text: str
    scenario_text: str
    question: str


class AuditEntry(BaseModel):
    timestamp: str
    policy_type: str
    question: str
    risk_level: str
    escalation_required: bool
    model: str
    demo_mode: bool
    pii_detected: bool
