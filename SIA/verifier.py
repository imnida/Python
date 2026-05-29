"""Verifier interface — deterministic per-instance reward computation."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Verifier(ABC):
    """Base class for task verifiers.

    A verifier scores a single model answer against ground truth and returns
    a scalar reward in [0, 1].
    """

    @abstractmethod
    def score(self, prediction: Any, ground_truth: Any) -> float:
        """Return a scalar reward for prediction given ground_truth."""

    def batch_score(self, predictions: list[Any], ground_truths: list[Any]) -> list[float]:
        return [self.score(p, g) for p, g in zip(predictions, ground_truths)]


class ExactMatchVerifier(Verifier):
    """1.0 if prediction == ground_truth (after normalisation), else 0.0."""

    def score(self, prediction: Any, ground_truth: Any) -> float:
        return 1.0 if str(prediction).strip() == str(ground_truth).strip() else 0.0


class FunctionVerifier(Verifier):
    """Wraps an arbitrary callable as a verifier."""

    def __init__(self, fn):
        self._fn = fn

    def score(self, prediction: Any, ground_truth: Any) -> float:
        return float(self._fn(prediction, ground_truth))


class ThresholdVerifier(Verifier):
    """Binary reward: 1.0 if a numeric metric exceeds a threshold."""

    def __init__(self, threshold: float, higher_is_better: bool = True):
        self.threshold = threshold
        self.higher_is_better = higher_is_better

    def score(self, prediction: float, ground_truth: Any = None) -> float:
        if self.higher_is_better:
            return 1.0 if prediction >= self.threshold else prediction / self.threshold
        return 1.0 if prediction <= self.threshold else self.threshold / max(prediction, 1e-9)
