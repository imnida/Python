"""Meta-Agent M: generates the initial task-specific scaffold A1 from U and R.

Uses Claude Sonnet 4.6 as the LLM backbone (§5.2).
"""
from __future__ import annotations

import textwrap
from typing import Any

import anthropic

_META_SYSTEM = textwrap.dedent("""
    You are the Meta-Agent in the SIA (Self-Improving AI) framework.
    Your job is to generate a complete, runnable Python scaffold for a task-specific agent.

    The scaffold must:
    1. Accept a task instance and produce an answer.
    2. Include a system prompt, tool-dispatch logic, and answer extraction.
    3. Expose a `run(instance: dict) -> dict` function that returns
       {"answer": <prediction>, "trajectory_step": <Step dict>}.
    4. Be self-contained (all imports at the top, no undefined references).

    Output ONLY valid Python source code — no prose, no markdown fences.
""").strip()

_META_USER_TMPL = textwrap.dedent("""
    Task specification:
    {task_spec}

    Reference implementations (if any):
    {reference_impls}

    Diverse sample instances to avoid overfitting the scaffold to a single case:
    {sample_instances}

    Generate the initial scaffold A1.
""").strip()


class MetaAgent:
    """Generates A1 = M(U, R)."""

    def __init__(self, model: str = "claude-sonnet-4-6", max_tokens: int = 8192):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens

    def generate_scaffold(
        self,
        task_spec: str,
        reference_impls: str = "",
        sample_instances: list[dict[str, Any]] | None = None,
    ) -> str:
        """Return the source code of the initial scaffold A1."""
        samples_text = _format_samples(sample_instances or [])
        user_msg = _META_USER_TMPL.format(
            task_spec=task_spec,
            reference_impls=reference_impls or "(none provided)",
            sample_instances=samples_text,
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=_META_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        return response.content[0].text.strip()


def _format_samples(samples: list[dict[str, Any]]) -> str:
    if not samples:
        return "(none provided)"
    lines = []
    for i, s in enumerate(samples[:5], 1):
        lines.append(f"Sample {i}: {s}")
    return "\n".join(lines)
