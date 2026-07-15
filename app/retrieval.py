"""Lightweight RAG retrieval — no vector DB needed for MVP1.

The pasted policy is split into clause-level chunks, each chunk is scored
against the scenario + question with a TF-IDF-weighted token overlap, and only
the top-k chunks are sent to the model. Chunk IDs flow through to the response
so every policy_basis item is a verifiable citation.
"""

import math
import re

from .schemas import RetrievedChunk

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "for", "on", "with", "is",
    "are", "be", "must", "any", "all", "by", "at", "as", "that", "this", "it",
    "its", "their", "our", "we", "can", "may", "not", "no", "before", "after",
    "has", "have", "was", "were", "will", "shall", "should", "would", "do",
    "does", "from", "into", "than", "been", "who", "which", "when", "while",
}


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in _STOPWORDS and len(t) > 2]


def chunk_policy(policy_text: str) -> list[str]:
    """Split on numbered clauses first, then blank lines, then sentences."""
    text = policy_text.strip()
    if not text:
        return []

    # Numbered clauses like "1. ..." / "2) ..." / "(3) ..." are the natural unit
    clause_split = re.split(r"(?m)^\s*(?:\(?\d+[\.\)]\s+)", text)
    clauses = [c.strip() for c in clause_split if c.strip()]
    if len(clauses) >= 3:
        return clauses

    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if len(paras) >= 3:
        return paras

    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    # Merge very short sentences into their neighbor so chunks carry context
    merged: list[str] = []
    for s in sentences:
        if merged and len(merged[-1]) < 120:
            merged[-1] = f"{merged[-1]} {s}"
        else:
            merged.append(s)
    return merged or [text]


def retrieve(policy_text: str, scenario_text: str, question: str, top_k: int = 6) -> list[RetrievedChunk]:
    chunks = chunk_policy(policy_text)
    if not chunks:
        return []

    query_tokens = _tokens(f"{scenario_text} {question}")
    if not query_tokens:
        return [RetrievedChunk(chunk_id=i + 1, text=c, score=0.0) for i, c in enumerate(chunks[:top_k])]

    n = len(chunks)
    chunk_token_sets = [set(_tokens(c)) for c in chunks]
    df = {t: sum(1 for s in chunk_token_sets if t in s) for t in set(query_tokens)}

    scored = []
    for i, token_set in enumerate(chunk_token_sets):
        score = 0.0
        for t in set(query_tokens):
            if t in token_set:
                score += math.log((n + 1) / (df.get(t, 0) + 1)) + 1.0
        if token_set:
            score /= math.sqrt(len(token_set))
        scored.append(RetrievedChunk(chunk_id=i + 1, text=chunks[i], score=round(score, 4)))

    scored.sort(key=lambda c: c.score, reverse=True)
    kept = scored[:top_k]
    # Present citations in document order for readability
    kept.sort(key=lambda c: c.chunk_id)
    return kept
