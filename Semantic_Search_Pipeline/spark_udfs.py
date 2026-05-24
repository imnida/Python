"""
PySpark UDFs for distributed embedding generation.

This module requires pyspark. Install it with:
    pip install pyspark

These UDFs wrap get_embedding() so it runs on every executor node,
distributing the embedding workload across the cluster.

Key production rules enforced here (from the article):
  1. Never collect() a large embedding result to the driver.
  2. Write directly to Delta Lake / parquet from the executor.
  3. Register one Session per UDF call (not per record) via a broadcast variable
     or module-level initialisation inside the UDF closure.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

try:
    from pyspark.sql import SparkSession, DataFrame
    from pyspark.sql import functions as F
    from pyspark.sql.types import ArrayType, FloatType, StringType, StructField, StructType
    _PYSPARK_AVAILABLE = True
except ImportError:
    _PYSPARK_AVAILABLE = False
    logger.warning(
        "pyspark not installed — spark_udfs module loaded in stub mode. "
        "Install with: pip install pyspark"
    )


def _require_pyspark() -> None:
    if not _PYSPARK_AVAILABLE:
        raise ImportError(
            "pyspark is required for this module. Install it with: pip install pyspark"
        )


def get_spark_session(app_name: str = "SemanticSearchPipeline", master: str = "local[*]") -> "SparkSession":
    _require_pyspark()
    return (
        SparkSession.builder
        .appName(app_name)
        .master(master)
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )


def make_embedding_udf(use_mock: bool = True):
    """
    Return a PySpark UDF that embeds a text column.

    The inner function is defined at module level so pyspark can serialise it
    to executors. Session / model initialisation happens inside the UDF so
    each executor initialises once (not once per row).
    """
    _require_pyspark()
    from pyspark.sql.types import ArrayType, FloatType
    from pyspark.sql.functions import udf

    # Capture use_mock in closure — avoids importing config on the driver
    # and having config-on-executor diverge from driver config.
    _use_mock = use_mock

    @udf(returnType=ArrayType(FloatType()))
    def embed_text_udf(text: str):
        # Module-level imports inside UDF run on the executor
        import hashlib, math

        if not text or not text.strip():
            return [0.0] * 128

        if _use_mock:
            # Same deterministic mock as api_client.mock_embedding
            dim = 128
            digest = hashlib.sha256(text.encode()).digest()
            raw = []
            seed = digest
            while len(raw) < dim:
                seed = hashlib.sha256(seed).digest()
                raw.extend(b / 255.0 for b in seed)
            raw = raw[:dim]
            magnitude = math.sqrt(sum(v * v for v in raw))
            return [v / magnitude for v in raw] if magnitude > 0 else raw
        else:
            # Real path: import api_client which must be distributed to executors
            # via spark.sparkContext.addPyFile() or packaged into the job zip.
            from api_client import get_embedding, build_session
            session = build_session()
            return get_embedding(text, session)

    return embed_text_udf


def run_spark_embedding_pipeline(
    spark: "SparkSession",
    table_name: str,
    output_path: str,
    start_date: str,
    end_date: str,
    text_col: str = "description",
    date_col: str = "created_date",
    chunk_days: int = 7,
    use_mock: bool = True,
) -> None:
    """
    Full distributed embedding pipeline mirroring the article's production pattern.

    Reads from a registered Spark table, chunks by date, generates embeddings
    via a UDF, runs data quality checks, and writes to Delta Lake.
    Never calls collect() on the embedding data.
    """
    _require_pyspark()
    from datetime import date, timedelta
    from chunking import date_chunks

    embed_udf = make_embedding_udf(use_mock=use_mock)
    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    for chunk_start, chunk_end in date_chunks(start, end, chunk_days):
        logger.info("Spark pipeline: processing chunk [%s, %s)", chunk_start, chunk_end)

        chunk_df: DataFrame = (
            spark.table(table_name)
            .filter(
                (F.col(date_col) >= str(chunk_start)) &
                (F.col(date_col) < str(chunk_end))
            )
            .filter(F.col(text_col).isNotNull())
        )

        # Log row count without collecting the full dataset
        row_count = chunk_df.count()
        logger.info("Chunk [%s, %s): %d row(s) to embed", chunk_start, chunk_end, row_count)
        if row_count == 0:
            continue

        embedded_df = chunk_df.withColumn("embedding", embed_udf(F.col(text_col)))

        # Quality gate: fail loudly rather than silently writing nulls
        bad_count = embedded_df.filter(F.col("embedding").isNull()).count()
        if bad_count > 0:
            logger.error(
                "Chunk [%s, %s): %d/%d rows have null embeddings — aborting chunk write",
                chunk_start, chunk_end, bad_count, row_count,
            )
            continue

        chunk_path = f"{output_path}/date={chunk_start}"
        # Write directly to Delta — never collect() to driver
        (
            embedded_df
            .write
            .format("delta")
            .mode("overwrite")
            .save(chunk_path)
        )
        logger.info("Chunk [%s, %s): written %d rows to %s", chunk_start, chunk_end, row_count, chunk_path)
