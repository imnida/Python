"""
End-to-end runnable demo of the semantic search pipeline.

Runs entirely locally — no Spark cluster, no external API key required.
Set USE_MOCK_EMBEDDINGS=false and EMBEDDING_ENDPOINT=<url> to switch to
a real embedding endpoint.

Usage:
    python demo.py
    ENABLE_PROFILING=true python demo.py
    LOG_LEVEL=DEBUG python demo.py
"""
from __future__ import annotations

import sys
from datetime import date

from logging_config import configure_logging
from synthetic_data import generate_tickets
from local_pipeline import LocalSemanticSearchPipeline

BANNER = """
╔══════════════════════════════════════════════════════════╗
║   Semantic Search Pipeline — Notebook-to-Production Demo ║
║   Patterns: chunking · retry logic · data quality        ║
╚══════════════════════════════════════════════════════════╝
"""

DEMO_QUERIES = [
    "I was charged the wrong amount on my invoice",
    "the app keeps crashing when I try to export",
    "I want to add more users to my team",
    "my parcel has not arrived yet",
    "can you add dark mode to the interface",
    "login problems with two factor authentication",
]


def print_results(query: str, results: list) -> None:
    print(f"\n  Query: \"{query}\"")
    print(f"  {'─' * 60}")
    for rank, r in enumerate(results, start=1):
        category = r.metadata.get("category", "?")
        text = r.metadata.get("description", "")[:70]
        print(f"  {rank}. [{r.score:.3f}] ({category}) {text}")


def main() -> None:
    logger = configure_logging()
    print(BANNER)

    # ── Stage 1: Ingest ───────────────────────────────────────────────
    print("► Generating synthetic support tickets...")
    records = generate_tickets(n=250, start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
    category_counts = {}
    for r in records:
        category_counts[r["category"]] = category_counts.get(r["category"], 0) + 1
    print(f"  {len(records)} tickets generated | categories: {category_counts}")

    # ── Stages 2–5: Chunk → Embed → Validate → Index ─────────────────
    print("\n► Running pipeline (chunking · embedding · quality checks · indexing)...")
    pipeline = LocalSemanticSearchPipeline(
        output_path="/tmp/semantic_search/embeddings",
        vector_store_path="/tmp/semantic_search/vectors",
        chunk_days=14,
    )
    store = pipeline.run(
        records=records,
        start_date=date(2024, 1, 1),
        end_date=date(2024, 3, 31),
    )
    print(f"\n  Vector store size: {len(store)} embeddings indexed")

    # ── Search ────────────────────────────────────────────────────────
    print("\n► Semantic search queries")
    print("  " + "═" * 62)
    for query in DEMO_QUERIES:
        results = pipeline.search(query, top_k=3)
        print_results(query, results)

    # ── Persistence round-trip ────────────────────────────────────────
    print("\n► Testing persistence (save → load → search)...")
    from vector_store import VectorStore
    from api_client import get_embedding

    loaded_store = VectorStore.load("/tmp/semantic_search/vectors")
    test_vec = get_embedding("I need a refund for a duplicate charge")
    reload_results = loaded_store.search(test_vec, top_k=2)
    print(f"  Loaded store size: {len(loaded_store)}")
    print(f"  Top result after reload: {reload_results[0]}")

    print("\n✓ Demo complete.\n")


if __name__ == "__main__":
    main()
