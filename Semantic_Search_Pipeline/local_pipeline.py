"""
Local (pandas-based) semantic search pipeline.

Mirrors all production patterns from the article — chunking, retry logic,
data quality checks, logging — but runs without Spark or a real embedding
endpoint. Use this for local development and integration testing before
promoting to the Spark pipeline.

Pipeline stages (matching the article's 5-step ML pipeline):
  1. Ingest   — load records (synthetic data in the demo)
  2. Transform — chunk by date, clean text
  3. Embed    — call get_embedding() per record (mock or real API)
  4. Validate  — data quality checks pre- and post-embedding
  5. Serve    — write to VectorStore; expose search()
"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Optional

from api_client import build_session, get_embedding
from chunking import chunk_records
from config import config
from data_quality import check_embeddings, check_records
from logging_config import get_logger
from vector_store import VectorStore

logger = get_logger(__name__)


class LocalSemanticSearchPipeline:
    """
    End-to-end semantic search pipeline that runs on a single machine.
    """

    def __init__(
        self,
        output_path: str = config.output_path,
        vector_store_path: str = config.vector_store_path,
        chunk_days: int = config.chunk_days,
    ) -> None:
        self.output_path = output_path
        self.vector_store_path = vector_store_path
        self.chunk_days = chunk_days
        self.store = VectorStore(store_path=vector_store_path)
        self._session = None   # lazy — only built when USE_MOCK_EMBEDDINGS=false

    # ------------------------------------------------------------------
    # Stage 1 + 2: Ingest & Transform
    # ------------------------------------------------------------------

    def _preprocess(self, records: list[dict], text_field: str = "description") -> list[dict]:
        """Strip whitespace; drop records where text is missing."""
        clean = []
        dropped = 0
        for r in records:
            text = r.get(text_field, "")
            if text is None or str(text).strip() == "":
                dropped += 1
                continue
            clean.append({**r, text_field: str(text).strip()})
        if dropped:
            logger.warning("Preprocessing dropped %d record(s) with empty/null text", dropped)
        return clean

    # ------------------------------------------------------------------
    # Stage 3: Embed
    # ------------------------------------------------------------------

    def _embed_batch(self, records: list[dict], text_field: str = "description") -> list[dict]:
        if not config.use_mock_embeddings and self._session is None:
            self._session = build_session()

        embedded = []
        for r in records:
            text = r[text_field]
            embedding = get_embedding(text, self._session)
            embedded.append({**r, "embedding": embedding})
        return embedded

    # ------------------------------------------------------------------
    # Stage 4: Validate
    # ------------------------------------------------------------------

    @staticmethod
    def _quality_gate(records: list[dict], report_label: str) -> bool:
        report = check_records(records)
        if not report.passed:
            logger.error("[%s] Pre-embedding quality gate FAILED: %s", report_label, report.summarise())
            return False
        return True

    @staticmethod
    def _embedding_quality_gate(records: list[dict], report_label: str, expected_dim: int) -> bool:
        report = check_embeddings(records, expected_dim=expected_dim)
        if not report.passed:
            logger.error("[%s] Post-embedding quality gate FAILED: %s", report_label, report.summarise())
            return False
        return True

    # ------------------------------------------------------------------
    # Stage 5: Serve / write
    # ------------------------------------------------------------------

    def _write_chunk(self, embedded: list[dict], chunk_start: date, chunk_end: date) -> None:
        path = Path(self.output_path) / f"date={chunk_start}"
        path.mkdir(parents=True, exist_ok=True)
        out_file = path / "records.jsonl"
        with open(out_file, "w") as f:
            for r in embedded:
                f.write(json.dumps(r, default=str) + "\n")
        logger.info(
            "Chunk [%s, %s): wrote %d record(s) to %s",
            chunk_start, chunk_end, len(embedded), out_file,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(
        self,
        records: list[dict],
        start_date: date,
        end_date: date,
        text_field: str = "description",
        date_field: str = "created_date",
    ) -> VectorStore:
        """
        Run the full pipeline over *records* for [start_date, end_date).
        Returns the populated VectorStore.
        """
        logger.info(
            "Pipeline starting: %d records, %s → %s, chunk_days=%d",
            len(records), start_date, end_date, self.chunk_days,
        )

        total_embedded = 0
        for (chunk_start, chunk_end), chunk in chunk_records(
            records, date_field, start_date, end_date, self.chunk_days
        ):
            label = f"{chunk_start}:{chunk_end}"

            if not chunk:
                logger.info("Chunk [%s, %s): empty — skipping", chunk_start, chunk_end)
                continue

            # Stage 2: clean
            clean = self._preprocess(chunk, text_field)

            # Stage 4a: pre-embedding quality gate
            if not self._quality_gate(clean, label):
                logger.warning("Chunk [%s, %s): skipped after quality failure", chunk_start, chunk_end)
                continue

            # Stage 3: embed
            embedded = self._embed_batch(clean, text_field)

            # Stage 4b: post-embedding quality gate
            if not self._embedding_quality_gate(embedded, label, config.embedding_dim):
                logger.warning("Chunk [%s, %s): skipped after embedding quality failure", chunk_start, chunk_end)
                continue

            # Stage 5a: persist raw output
            self._write_chunk(embedded, chunk_start, chunk_end)

            # Stage 5b: load into vector store
            store_records = [
                {"id": r["id"], "embedding": r["embedding"], **{k: r[k] for k in r if k not in ("embedding",)}}
                for r in embedded
            ]
            self.store.add_batch(store_records)
            total_embedded += len(embedded)

            # Optional profiling (expensive at scale — disabled by default)
            if config.enable_profiling:
                categories = {}
                for r in embedded:
                    cat = r.get("category", "unknown")
                    categories[cat] = categories.get(cat, 0) + 1
                logger.info("Chunk [%s, %s) category distribution: %s", chunk_start, chunk_end, categories)

        logger.info("Pipeline complete: %d record(s) embedded and indexed", total_embedded)

        if self.vector_store_path:
            self.store.save(self.vector_store_path)

        return self.store

    def search(self, query: str, top_k: int = 5) -> list:
        """
        Semantic search: embed *query* and return the top_k most similar records.
        """
        if len(self.store) == 0:
            raise RuntimeError("Pipeline has not been run yet — call run() first or load a saved store")

        query_vec = get_embedding(query, self._session)
        results = self.store.search(query_vec, top_k=top_k)
        logger.info("Query %r → %d result(s)", query[:50], len(results))
        return results
