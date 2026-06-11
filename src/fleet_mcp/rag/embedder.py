"""Pluggable embeddings.

`HashingEmbedder` is a deterministic, offline bag-of-words hashing embedder. It
is intentionally simple: no model download, no API key, no network. It is good
enough to demonstrate semantic-ish retrieval over a small knowledge base and to
keep the whole project runnable for free.

For production-grade retrieval you would implement `Embedder` against a real
embedding model. A sketch of a Bedrock (Cohere/Titan) embedder is included and
commented so the seam is obvious.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class Embedder(Protocol):
    """Turn text into a fixed-length, L2-normalized vector."""

    dimensions: int

    def embed(self, text: str) -> list[float]: ...


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class HashingEmbedder:
    """Feature-hashing embedder. Stable across runs, zero dependencies."""

    def __init__(self, dimensions: int = 256) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vec = [0.0] * self.dimensions
        tokens = _tokenize(text)
        if not tokens:
            return vec
        for tok in tokens:
            # Hash unigrams and bigrams for a little more signal.
            self._add(vec, tok)
        for a, b in zip(tokens, tokens[1:]):
            self._add(vec, f"{a}_{b}")
        return _l2_normalize(vec)

    def _add(self, vec: list[float], feature: str) -> None:
        h = int.from_bytes(hashlib.md5(feature.encode()).digest()[:8], "big")
        idx = h % self.dimensions
        sign = 1.0 if (h >> 1) % 2 == 0 else -1.0
        vec[idx] += sign


def _l2_normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


# --- Production seam (commented) -----------------------------------------
# class BedrockEmbedder:
#     """Example: amazon.titan-embed-text-v2 or cohere.embed-english-v3 via Bedrock."""
#
#     dimensions = 1024
#
#     def __init__(self, client, model_id="amazon.titan-embed-text-v2:0"):
#         self._client = client          # boto3 bedrock-runtime client
#         self._model_id = model_id
#
#     def embed(self, text: str) -> list[float]:
#         import json
#         resp = self._client.invoke_model(
#             modelId=self._model_id,
#             body=json.dumps({"inputText": text}),
#         )
#         return json.loads(resp["body"].read())["embedding"]
