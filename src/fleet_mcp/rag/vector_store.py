"""A minimal in-memory vector store: cosine similarity over embedded documents.

This is deliberately small (a few hundred lines of stdlib) so the architecture
is legible. In production you would point the same interface at pgvector,
OpenSearch, Pinecone, etc. — the tool layer doesn't care.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from fleet_mcp.rag.embedder import Embedder


@dataclass
class Document:
    id: str
    text: str
    metadata: dict = field(default_factory=dict)
    embedding: list[float] | None = None


@dataclass
class SearchHit:
    document: Document
    score: float


def _cosine(a: list[float], b: list[float]) -> float:
    # Both vectors are L2-normalized by the embedder, so dot product == cosine.
    return sum(x * y for x, y in zip(a, b))


class InMemoryVectorStore:
    def __init__(self, embedder: Embedder) -> None:
        self._embedder = embedder
        self._docs: list[Document] = []

    def add(self, documents: list[Document]) -> None:
        for doc in documents:
            if doc.embedding is None:
                doc.embedding = self._embedder.embed(doc.text)
            self._docs.append(doc)

    def search(self, query: str, top_k: int = 3, min_score: float = 0.0) -> list[SearchHit]:
        if not self._docs:
            return []
        q = self._embedder.embed(query)
        scored = [SearchHit(d, _cosine(q, d.embedding or [])) for d in self._docs]
        scored.sort(key=lambda h: h.score, reverse=True)
        return [h for h in scored[:top_k] if h.score > min_score]

    def __len__(self) -> int:
        return len(self._docs)
