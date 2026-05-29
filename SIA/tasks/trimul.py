"""AlphaEvolve TriMul: CUDA kernel optimisation for protein structure prediction (§6.3.2).

The triangular multiplicative update (TriMul) is a core operation in
AlphaFold2's Evoformer module.  The task asks an agent to write a custom
CUDA kernel for this operation on an H100 GPU.

Benchmark: AlphaEvolve (Novikov et al., 2025).
Metric: score = 1500 / runtime_µs  (higher is faster).
Previous SOTA: 1.292 (≈ 1,161 µs)
SIA-H:  0.120 (≈ 12,483 µs)   [harness only]
SIA-W+H: 1.475 (≈ 1,017 µs)  [harness + weight updates]
"""
from __future__ import annotations

from typing import Any

from ..verifier import Verifier

TASK_SPEC = """
Task: CUDA Kernel Optimisation — AlphaFold2 Triangular Multiplicative Update (TriMul)

The triangular multiplicative update kernel propagates pairwise residue-interaction
features during protein structure prediction.  It is memory-bandwidth-limited due to
the triangular sparsity structure inducing warp divergence and cache misses.

Achieving high throughput requires H100-specific knowledge:
  - Tensor core scheduling
  - Shared-memory tiling (fp16 or fp32 accumulation)
  - Register pressure management
  - Block-size selection for the H100 SM configuration

Input:  Fixed tensor shapes (the evaluation harness supplies these at runtime).
Output: A compilable Triton or CUDA kernel that performs the TriMul operation
        correctly and as fast as possible.

Metric: score = 1500 / runtime_µs  (higher = faster; measured via H100 timing harness).
Verifier: H100 timing harness returning median runtime over 100 warm runs.
""".strip()

REFERENCE_IMPL = """
# Minimal Triton kernel stub (starting point for the Meta-Agent)
import triton
import triton.language as tl
import torch

@triton.jit
def trimul_kernel(
    a_ptr, b_ptr, g_ptr, out_ptr,
    N, K,
    stride_an, stride_ak,
    stride_bn, stride_bk,
    stride_on,
    BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
):
    pid = tl.program_id(0)
    n_off = pid * BLOCK_N + tl.arange(0, BLOCK_N)
    k_off = tl.arange(0, BLOCK_K)
    a = tl.load(a_ptr + n_off[:, None] * stride_an + k_off[None, :] * stride_ak)
    b = tl.load(b_ptr + n_off[:, None] * stride_bn + k_off[None, :] * stride_bk)
    g = tl.load(g_ptr + n_off[:, None] * stride_an + k_off[None, :] * stride_ak)
    out = tl.sum(a * b * g, axis=1)
    tl.store(out_ptr + n_off * stride_on, out)

def run(instance: dict) -> dict:
    return {"answer": None, "prompt": str(instance), "response": "", "tool_calls": []}
"""


class TriMulVerifier(Verifier):
    """Scores a kernel by its runtime; score = 1500 / runtime_µs."""

    def score(self, prediction: Any, ground_truth: Any = None) -> float:
        try:
            runtime_us = float(prediction)
            if runtime_us <= 0:
                return 0.0
            return 1500.0 / runtime_us
        except (TypeError, ValueError):
            return 0.0


class TriMulTask:
    """Task wrapper for AlphaEvolve TriMul."""

    task_spec: str = TASK_SPEC
    reference_impl: str = REFERENCE_IMPL
    verifier: TriMulVerifier = TriMulVerifier()
    previous_sota: float = 1.292

    @staticmethod
    def make_instance(input_shapes: dict[str, Any], idx: int = 0) -> dict[str, Any]:
        return {"id": str(idx), "input_shapes": input_shapes, "ground_truth": None}

    @staticmethod
    def sample_instances() -> list[dict[str, Any]]:
        return [
            {"id": "0", "input_shapes": {"N": 256, "K": 128}, "ground_truth": None},
        ]
