"""
Date-based chunking utilities.

Chunking serves two production goals:
  1. Limits compute per run — avoids single giant Spark jobs.
  2. Enables resumability — a failed chunk reruns without touching already-written data.
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Generator, Iterator

logger = logging.getLogger(__name__)


def date_chunks(
    start_date: date,
    end_date: date,
    chunk_days: int = 7,
) -> Generator[tuple[date, date], None, None]:
    """
    Yields (chunk_start, chunk_end) pairs covering [start_date, end_date).

    The final window is clipped so chunk_end never exceeds end_date.
    Empty ranges (start_date >= end_date) produce no chunks.
    """
    if start_date >= end_date:
        logger.warning(
            "date_chunks called with start_date=%s >= end_date=%s — no chunks produced",
            start_date,
            end_date,
        )
        return

    current = start_date
    chunk_num = 0
    while current < end_date:
        chunk_end = min(current + timedelta(days=chunk_days), end_date)
        chunk_num += 1
        logger.debug("Chunk %d: [%s, %s)", chunk_num, current, chunk_end)
        yield current, chunk_end
        current = chunk_end

    logger.info(
        "date_chunks: %d chunk(s) spanning %s → %s (chunk_days=%d)",
        chunk_num,
        start_date,
        end_date,
        chunk_days,
    )


def chunk_records(
    records: list[dict],
    date_field: str,
    start_date: date,
    end_date: date,
    chunk_days: int = 7,
) -> Iterator[tuple[tuple[date, date], list[dict]]]:
    """
    Filter *records* (list of dicts) by date_field for each chunk window.
    Yields (chunk_window, matching_records) pairs.

    Used by the local/pandas pipeline; the Spark pipeline uses date_chunks
    directly with a DataFrame filter (see spark_pipeline.py).
    """
    for chunk_start, chunk_end in date_chunks(start_date, end_date, chunk_days):
        window = (chunk_start, chunk_end)
        subset = [
            r
            for r in records
            if chunk_start <= r[date_field] < chunk_end
        ]
        logger.info(
            "Chunk [%s, %s): %d record(s)", chunk_start, chunk_end, len(subset)
        )
        yield window, subset
