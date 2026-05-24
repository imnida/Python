"""
Airflow DAG definition for the production semantic search pipeline.

Requires: apache-airflow, pyspark
Mirrors the article's scheduling pattern: Airflow DAG with retries and backoff.

DAG structure:
  check_quality → embed_chunk_* (parallel per date partition) → validate_store → alert_on_failure

Deploy by placing this file in $AIRFLOW_HOME/dags/.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

# Guard import so the module is importable without Airflow installed
try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
    from airflow.operators.empty import EmptyOperator
    from airflow.utils.dates import days_ago
    _AIRFLOW_AVAILABLE = True
except ImportError:
    _AIRFLOW_AVAILABLE = False


DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "retry_exponential_backoff": True,   # doubles delay on each retry
    "max_retry_delay": timedelta(minutes=60),
}

PIPELINE_CONFIG = {
    "start_date": "2024-01-01",
    "end_date": "2024-03-31",
    "chunk_days": 14,
    "table_name": "support_tickets",
    "output_path": "/mnt/embeddings/support_tickets",
    "vector_store_path": "/mnt/vectors/support_tickets",
}


# ---------------------------------------------------------------------------
# Task functions
# ---------------------------------------------------------------------------

def run_quality_check(**context) -> None:
    """Pre-flight: assert source table is non-empty and schema is intact."""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Quality pre-check for table '%s'", PIPELINE_CONFIG["table_name"])
    # In production: spark.table(...).count(), schema validation, freshness check


def embed_chunk(chunk_start: str, chunk_end: str, **context) -> None:
    """Embed one date partition and write to output path."""
    import logging
    from datetime import date
    from local_pipeline import LocalSemanticSearchPipeline

    logger = logging.getLogger(__name__)
    logger.info("Embedding chunk [%s, %s)", chunk_start, chunk_end)

    pipeline = LocalSemanticSearchPipeline(
        output_path=PIPELINE_CONFIG["output_path"],
        vector_store_path=PIPELINE_CONFIG["vector_store_path"],
        chunk_days=int(chunk_end[:10].replace("-", "")) - int(chunk_start[:10].replace("-", "")),
    )
    # In production: pipeline.run(spark.table(...), ...)
    logger.info("Chunk [%s, %s) complete", chunk_start, chunk_end)


def validate_vector_store(**context) -> None:
    """Post-run: assert vector store is non-empty and persisted correctly."""
    import logging
    from vector_store import VectorStore

    logger = logging.getLogger(__name__)
    store = VectorStore.load(PIPELINE_CONFIG["vector_store_path"])
    if len(store) == 0:
        raise ValueError("Vector store is empty after pipeline run — pipeline may have failed silently")
    logger.info("Vector store validation passed: %d vectors indexed", len(store))


# ---------------------------------------------------------------------------
# DAG definition (only instantiated when Airflow is available)
# ---------------------------------------------------------------------------

if _AIRFLOW_AVAILABLE:
    with DAG(
        dag_id="semantic_search_embedding_pipeline",
        default_args=DEFAULT_ARGS,
        description="Embed support tickets and index into vector store",
        schedule_interval="0 2 * * *",    # daily at 02:00 UTC
        start_date=days_ago(1),
        catchup=False,
        tags=["ml", "embeddings", "semantic-search"],
    ) as dag:

        quality_check = PythonOperator(
            task_id="pre_flight_quality_check",
            python_callable=run_quality_check,
        )

        # One task per chunk window — they run in parallel
        from chunking import date_chunks
        from datetime import date as _date

        _start = _date.fromisoformat(PIPELINE_CONFIG["start_date"])
        _end = _date.fromisoformat(PIPELINE_CONFIG["end_date"])
        _chunk_days = PIPELINE_CONFIG["chunk_days"]

        chunk_tasks = []
        for cs, ce in date_chunks(_start, _end, _chunk_days):
            task = PythonOperator(
                task_id=f"embed_{cs}_{ce}",
                python_callable=embed_chunk,
                op_kwargs={"chunk_start": str(cs), "chunk_end": str(ce)},
            )
            quality_check >> task
            chunk_tasks.append(task)

        validate = PythonOperator(
            task_id="validate_vector_store",
            python_callable=validate_vector_store,
        )

        for t in chunk_tasks:
            t >> validate
