"""MAGIC scRNA-seq Denoising: Single-Cell RNA Imputation (§6.3.3).

MAGIC (Markov Affinity-based Graph Imputation of Cells) addresses the high
sparsity of scRNA-seq count matrices by constructing a k-nearest-neighbour
graph and diffusing expression values across graph neighbours.

The task asks an agent to tune MAGIC's coupled hyperparameters on pancreas
scRNA-seq data (Baron et al., 2016).

Benchmark: MAGIC (van Dijk et al., 2018).
Metric: mse_norm ∈ [0, 1], higher = better (1.0 = perfect imputation).
Previous SOTA: 0.240
SIA-H:   0.241  [harness only]
SIA-W+H: 0.289  [harness + weight updates]

Key SIA-W+H insight: a two-line post-processing step (np.clip + np.rint)
that rounds imputed counts to non-negative integers, enforcing a biological
invariant that the harness never generated. (§6.3.3)
"""
from __future__ import annotations

from typing import Any

import numpy as np

from ..verifier import Verifier

TASK_SPEC = """
Task: MAGIC scRNA-seq Hyperparameter Optimisation and Imputation

Single-cell RNA sequencing produces highly sparse count matrices (many true
non-zero counts observed as zero due to technical dropout).  MAGIC imputes
missing signal by:
  1. Building a k-nearest-neighbour graph over cells.
  2. Computing Markov transition probabilities.
  3. Diffusing expression values across graph neighbours.

Coupled hyperparameters to optimise:
  k     — number of neighbours (too small: overfits cell noise; too large: over-smoothing)
  t     — diffusion steps (controls diffusion depth)
  alpha — kernel bandwidth (Gaussian kernel parameter)

Additional preprocessing choices:
  - Library-size normalisation (CPM)
  - log1p transform
  - Gene selection / filtering

Dataset: Pancreas scRNA-seq (Baron et al., 2016).
Metric:  mse_norm — normalised reconstruction MSE against ground truth
         (higher is better; 1.0 = perfect imputation).

Biological invariant: imputed counts must be non-negative integers.
  Post-process with: imputed = np.clip(np.rint(imputed), 0, None)
""".strip()

REFERENCE_IMPL = """
import magic
import numpy as np

DEFAULT_PARAMS = {"knn": 5, "t": 3, "decay": 1}

def run(instance: dict) -> dict:
    X = instance.get("X")  # raw count matrix
    params = instance.get("params", DEFAULT_PARAMS)
    if X is None:
        return {"answer": None, "prompt": str(instance), "response": "", "tool_calls": []}
    try:
        magic_op = magic.MAGIC(**params)
        X_magic = magic_op.fit_transform(X)
        # Enforce biological invariant
        X_magic = np.clip(np.rint(X_magic), 0, None)
        return {
            "answer": X_magic,
            "prompt": str(params),
            "response": str(params),
            "tool_calls": [],
        }
    except Exception as e:
        return {"answer": None, "prompt": str(params), "response": str(e), "tool_calls": []}
"""


class SCRNASeqVerifier(Verifier):
    """Computes mse_norm = 1 − MSE(prediction, ground_truth) / MSE(zeros, ground_truth).

    Higher is better; 1.0 means perfect reconstruction.
    """

    def score(self, prediction: Any, ground_truth: Any) -> float:
        if prediction is None or ground_truth is None:
            return 0.0
        try:
            pred = np.asarray(prediction, dtype=float)
            gt = np.asarray(ground_truth, dtype=float)
            mse_pred = float(np.mean((pred - gt) ** 2))
            mse_zero = float(np.mean(gt ** 2))
            if mse_zero < 1e-12:
                return 1.0 if mse_pred < 1e-12 else 0.0
            return float(np.clip(1.0 - mse_pred / mse_zero, 0.0, 1.0))
        except Exception:
            return 0.0


class SCRNASeqTask:
    """Task wrapper for MAGIC scRNA-seq denoising."""

    task_spec: str = TASK_SPEC
    reference_impl: str = REFERENCE_IMPL
    verifier: SCRNASeqVerifier = SCRNASeqVerifier()
    previous_sota: float = 0.240

    @staticmethod
    def make_instance(X: Any, X_ground_truth: Any, idx: int = 0) -> dict[str, Any]:
        return {
            "id": str(idx),
            "X": X,
            "ground_truth": X_ground_truth,
            "params": {"knn": 5, "t": 3, "decay": 1},
        }

    @staticmethod
    def sample_instances() -> list[dict[str, Any]]:
        rng = np.random.default_rng(42)
        X = rng.poisson(lam=1.0, size=(50, 20)).astype(float)
        gt = rng.poisson(lam=2.0, size=(50, 20)).astype(float)
        return [{"id": "0", "X": X.tolist(), "ground_truth": gt.tolist(), "params": {"knn": 5, "t": 3, "decay": 1}}]
