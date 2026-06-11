"""Tests for the RAG vector store and knowledge base."""

from fleet_mcp.rag import HashingEmbedder, build_knowledge_base
from fleet_mcp.rag.vector_store import Document, InMemoryVectorStore


def test_embedder_is_deterministic_and_normalized():
    emb = HashingEmbedder(dimensions=64)
    a = emb.embed("cylinder misfire")
    b = emb.embed("cylinder misfire")
    assert a == b
    # L2 norm ~ 1 for non-empty text
    assert abs(sum(x * x for x in a) - 1.0) < 1e-6


def test_vector_store_ranks_relevant_doc_first():
    store = InMemoryVectorStore(HashingEmbedder())
    store.add(
        [
            Document(id="1", text="A misfire on cylinder 1 is caused by spark plugs or coils."),
            Document(id="2", text="Tire rotation should happen every 5000 miles."),
        ]
    )
    hits = store.search("what causes a cylinder misfire", top_k=1)
    assert hits and hits[0].document.id == "1"


def test_knowledge_base_loads_and_retrieves_dtc_guidance():
    kb = build_knowledge_base()
    assert len(kb) > 0
    hits = kb.search("is P0420 catalytic converter urgent", top_k=2)
    assert hits
    joined = " ".join(h.document.text for h in hits).lower()
    assert "catalyst" in joined or "p0420" in joined


def test_knowledge_base_finds_fuel_threshold_policy():
    kb = build_knowledge_base()
    hits = kb.search("what fuel percentage should trigger refueling", top_k=3)
    assert any("25%" in h.document.text for h in hits)
