"""Load the maintenance knowledge base into a vector store.

Knowledge lives as Markdown under `data/knowledge/`. Each `##` section becomes
one retrievable chunk. This keeps the corpus easy to edit (just add Markdown)
and keeps chunking predictable.
"""

from __future__ import annotations

from importlib import resources

from fleet_mcp.rag.embedder import Embedder, HashingEmbedder
from fleet_mcp.rag.vector_store import Document, InMemoryVectorStore


def _split_sections(name: str, markdown: str) -> list[Document]:
    docs: list[Document] = []
    current_title: str | None = None
    buffer: list[str] = []
    idx = 0

    def flush() -> None:
        nonlocal idx, buffer, current_title
        body = "\n".join(buffer).strip()
        if current_title and body:
            docs.append(
                Document(
                    id=f"{name}#{idx}",
                    text=f"{current_title}\n{body}",
                    metadata={"source": name, "title": current_title},
                )
            )
            idx += 1
        buffer = []

    for line in markdown.splitlines():
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
        else:
            buffer.append(line)
    flush()
    return docs


def build_knowledge_base(embedder: Embedder | None = None) -> InMemoryVectorStore:
    store = InMemoryVectorStore(embedder or HashingEmbedder())
    pkg = resources.files("fleet_mcp.data.knowledge")
    all_docs: list[Document] = []
    for entry in pkg.iterdir():
        if entry.name.endswith(".md"):
            all_docs.extend(_split_sections(entry.name, entry.read_text(encoding="utf-8")))
    store.add(all_docs)
    return store
