"""
In-memory vector store with cosine similarity search.

In production this is replaced by a purpose-built vector database
(Pinecone, Weaviate, pgvector, etc.). This implementation uses only numpy
so the full pipeline can run locally without infrastructure dependencies.

Cosine similarity is computed as dot product after L2 normalisation —
identical to how most managed vector databases operate with normalised vectors.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import numpy as np

from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class SearchResult:
    record_id: str
    score: float          # cosine similarity in [-1, 1]; higher = more similar
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        snippet = str(self.metadata.get("description", ""))[:60]
        return f"SearchResult(id={self.record_id!r}, score={self.score:.4f}, text={snippet!r})"


class VectorStore:
    """
    Append-only in-memory store. Persists to / loads from a directory of
    JSON + npy files so the pipeline can resume without re-embedding.
    """

    def __init__(self, store_path: Optional[str] = None) -> None:
        self._ids: list[str] = []
        self._matrix: Optional[np.ndarray] = None   # shape (n, dim)
        self._metadata: list[dict[str, Any]] = []
        self._store_path = store_path

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def add(
        self,
        record_id: str,
        embedding: list[float],
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        vec = np.array(embedding, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm          # ensure unit length

        self._ids.append(record_id)
        self._metadata.append(metadata or {})

        if self._matrix is None:
            self._matrix = vec.reshape(1, -1)
        else:
            self._matrix = np.vstack([self._matrix, vec.reshape(1, -1)])

    def add_batch(self, records: list[dict]) -> None:
        """
        Convenience method: each dict must have 'id', 'embedding', and
        optionally any metadata fields.
        """
        for r in records:
            self.add(
                record_id=r["id"],
                embedding=r["embedding"],
                metadata={k: v for k, v in r.items() if k not in ("id", "embedding")},
            )
        logger.info("VectorStore: added %d record(s), total=%d", len(records), len(self._ids))

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def search(self, query_embedding: list[float], top_k: int = 5) -> list[SearchResult]:
        if self._matrix is None or len(self._ids) == 0:
            logger.warning("VectorStore.search called on empty store")
            return []

        query = np.array(query_embedding, dtype=np.float32)
        norm = np.linalg.norm(query)
        if norm > 0:
            query = query / norm

        # Cosine similarity == dot product for unit vectors
        scores: np.ndarray = self._matrix @ query
        top_k = min(top_k, len(self._ids))
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = [
            SearchResult(
                record_id=self._ids[i],
                score=float(scores[i]),
                metadata=self._metadata[i],
            )
            for i in top_indices
        ]
        logger.debug("Search returned %d result(s), top_score=%.4f", len(results), results[0].score if results else 0)
        return results

    def __len__(self) -> int:
        return len(self._ids)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: Optional[str] = None) -> None:
        target = Path(path or self._store_path or "/tmp/vector_store")
        target.mkdir(parents=True, exist_ok=True)

        np.save(target / "matrix.npy", self._matrix if self._matrix is not None else np.array([]))
        (target / "ids.json").write_text(json.dumps(self._ids))
        (target / "metadata.json").write_text(json.dumps(self._metadata, default=str))
        logger.info("VectorStore saved %d vector(s) to %s", len(self._ids), target)

    @classmethod
    def load(cls, path: str) -> "VectorStore":
        target = Path(path)
        store = cls(store_path=path)
        matrix = np.load(target / "matrix.npy")
        store._matrix = matrix if matrix.size else None
        store._ids = json.loads((target / "ids.json").read_text())
        store._metadata = json.loads((target / "metadata.json").read_text())
        logger.info("VectorStore loaded %d vector(s) from %s", len(store._ids), target)
        return store
