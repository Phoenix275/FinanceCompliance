from app.retrieval import chunk_policy, retrieve
from app.samples import SAMPLES

POLICY = SAMPLES[0].policy_text  # numbered third-party policy


def test_numbered_policy_chunks_by_clause():
    chunks = chunk_policy(POLICY)
    assert len(chunks) >= 5
    assert any("beneficial ownership" in c.lower() for c in chunks)


def test_retrieval_ranks_relevant_clause():
    got = retrieve(POLICY, "Beneficial ownership disclosure is pending.", "Can we activate?")
    assert got, "should retrieve chunks"
    texts = " ".join(c.text.lower() for c in got)
    assert "beneficial ownership" in texts


def test_retrieval_empty_policy():
    assert retrieve("", "scenario", "question") == []


def test_unnumbered_policy_still_chunks():
    prose = (
        "All vendors must be screened before payment. Screening covers sanctions lists. "
        "Payments to unscreened vendors are prohibited.\n\n"
        "Invoices require a purchase order. Purchase orders above the threshold require dual approval."
    )
    chunks = chunk_policy(prose)
    assert len(chunks) >= 2


def test_chunk_ids_stable_and_in_document_order():
    got = retrieve(POLICY, SAMPLES[0].scenario_text, SAMPLES[0].question)
    ids = [c.chunk_id for c in got]
    assert ids == sorted(ids)
