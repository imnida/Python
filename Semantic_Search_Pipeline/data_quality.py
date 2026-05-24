"""
Data quality checks run at multiple points in the pipeline.

The article calls out data quality as a first-class pipeline concern.
Checks here are deliberately cheap — they run inline, not as a separate job.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class QualityReport:
    total_records: int = 0
    null_text_count: int = 0
    empty_text_count: int = 0
    missing_date_count: int = 0
    invalid_embedding_count: int = 0
    passed: bool = True
    warnings: list[str] = field(default_factory=list)

    @property
    def null_rate(self) -> float:
        return self.null_text_count / self.total_records if self.total_records else 0.0

    def summarise(self) -> str:
        return (
            f"QualityReport(total={self.total_records}, "
            f"null_text={self.null_text_count} ({self.null_rate:.1%}), "
            f"empty_text={self.empty_text_count}, "
            f"missing_date={self.missing_date_count}, "
            f"invalid_embedding={self.invalid_embedding_count}, "
            f"passed={self.passed})"
        )


def check_records(
    records: list[dict],
    text_field: str = "description",
    date_field: str = "created_date",
    null_threshold: float = 0.1,
) -> QualityReport:
    """
    Validate a batch of records before embedding.
    Marks the report as failed when null_rate exceeds null_threshold.
    """
    report = QualityReport(total_records=len(records))

    for r in records:
        text = r.get(text_field)
        if text is None:
            report.null_text_count += 1
        elif str(text).strip() == "":
            report.empty_text_count += 1

        if r.get(date_field) is None:
            report.missing_date_count += 1

    if report.null_rate > null_threshold:
        report.passed = False
        msg = (
            f"Null rate {report.null_rate:.1%} exceeds threshold {null_threshold:.1%} "
            f"in field '{text_field}'"
        )
        report.warnings.append(msg)
        logger.error(msg)
    elif report.null_text_count > 0:
        msg = f"{report.null_text_count} null(s) in '{text_field}' — below threshold, continuing"
        report.warnings.append(msg)
        logger.warning(msg)

    logger.info("Quality check: %s", report.summarise())
    return report


def check_embeddings(
    embedded_records: list[dict],
    embedding_field: str = "embedding",
    expected_dim: int = 128,
) -> QualityReport:
    """Validate that every record has a well-formed embedding vector."""
    report = QualityReport(total_records=len(embedded_records))

    for r in embedded_records:
        emb = r.get(embedding_field)
        if not isinstance(emb, list) or len(emb) != expected_dim:
            report.invalid_embedding_count += 1

    if report.invalid_embedding_count > 0:
        report.passed = False
        msg = f"{report.invalid_embedding_count} record(s) have invalid embeddings (expected dim={expected_dim})"
        report.warnings.append(msg)
        logger.error(msg)

    logger.info("Embedding quality check: %s", report.summarise())
    return report
