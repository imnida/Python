"""LawBench: 191-class Chinese Criminal Charge Classification (§6.3.1).

Given a factual case summary, the model must identify the correct criminal
charge from 191 distinct categories in Chinese statutory law.

Benchmark: Fei et al., 2023.
Metric: Top-1 accuracy on held-out test split.
Previous SOTA: 45.0%
SIA-H: 50.0%
SIA-W+H: 70.1%
"""
from __future__ import annotations

from typing import Any

from ..verifier import Verifier

TASK_SPEC = """
Task: Chinese Legal Charge Classification (LawBench 191-class)

Input:  A factual case summary in Chinese describing a criminal incident.
Output: Exactly one charge label from the 191 categories in Chinese statutory law.

Examples of fine-grained distinctions that must be handled:
- Theft sub-types: ordinary theft (盗窃), public-property theft, embezzlement (侵占)
- Assault grades: simple assault (故意伤害), aggravated, grievous bodily harm
- Fraud variants: ordinary fraud (诈骗), wire fraud, contract fraud

Dataset: 5,332 training / 913 test instances (all evaluations on held-out test split).
Metric: Top-1 accuracy (correct charge / total instances).
Verifier: exact string match against the gold charge label after normalisation.
""".strip()

REFERENCE_IMPL = """
# Minimal baseline: TF-IDF + LinearSVC pipeline (harness-discovered by SIA-H)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.pipeline import Pipeline
import json

def run(instance: dict) -> dict:
    # NOTE: This is a reference only; a real scaffold trains the pipeline first.
    return {
        "answer": None,
        "prompt": instance.get("text", ""),
        "response": "",
        "tool_calls": [],
    }
"""


class LawBenchVerifier(Verifier):
    """Exact-match verifier for LawBench charge labels."""

    def score(self, prediction: Any, ground_truth: Any) -> float:
        if prediction is None or ground_truth is None:
            return 0.0
        return 1.0 if _normalise(str(prediction)) == _normalise(str(ground_truth)) else 0.0


def _normalise(label: str) -> str:
    return label.strip().lower()


class LawBenchTask:
    """Task wrapper for LawBench."""

    task_spec: str = TASK_SPEC
    reference_impl: str = REFERENCE_IMPL
    verifier: LawBenchVerifier = LawBenchVerifier()
    previous_sota: float = 0.450

    @staticmethod
    def make_instance(text: str, charge: str, idx: int = 0) -> dict[str, Any]:
        return {"id": str(idx), "text": text, "ground_truth": charge}

    @staticmethod
    def sample_instances() -> list[dict[str, Any]]:
        """A handful of synthetic illustrative instances (not real LawBench data)."""
        return [
            {"id": "0", "text": "被告人趁被害人不备，将其钱包窃走。", "ground_truth": "盗窃"},
            {"id": "1", "text": "被告人持刀故意伤害被害人，致其轻伤。", "ground_truth": "故意伤害"},
            {"id": "2", "text": "被告人以非法占有为目的，虚构事实骗取他人财物。", "ground_truth": "诈骗"},
        ]
