"""Retrieval-Augmented Generation building blocks.

A tiny, dependency-free vector store with a pluggable `Embedder`. The default
`HashingEmbedder` runs offline with zero cost, so the RAG tool works out of the
box. Swap in a `BedrockEmbedder` (or any API embedder) by implementing the same
two-method interface — see `embedder.py`.
"""

from fleet_mcp.rag.embedder import Embedder, HashingEmbedder
from fleet_mcp.rag.knowledge_base import build_knowledge_base
from fleet_mcp.rag.vector_store import Document, InMemoryVectorStore

__all__ = [
    "Embedder",
    "HashingEmbedder",
    "Document",
    "InMemoryVectorStore",
    "build_knowledge_base",
]
