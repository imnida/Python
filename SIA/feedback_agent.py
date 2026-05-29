"""Feedback-Agent F: analyses trajectory τg and selects the next action.

Action choices (§5.1):
  - harness_update: synthesise an improved scaffold Ag+1 (weights fixed)
  - weight_update:  trigger an RL weight-update step (scaffold fixed)

Uses Claude Sonnet 4.6 as the LLM backbone (§5.2).
"""
from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from typing import Any

import anthropic

from .trajectory import Trajectory
from .weight_updates import ALGORITHM_REGISTRY, WeightUpdateAlgorithm

_FB_SYSTEM = textwrap.dedent("""
    You are the Feedback-Agent in the SIA (Self-Improving AI) framework.

    You receive:
    - The current scaffold source code (Ag)
    - The execution trajectory τg (structured log of prompts, responses, tool calls,
      extracted answers, and per-instance rewards)
    - Performance metrics Eg
    - The original task specification U
    - Sample task descriptions (to help avoid over-fitting fixes to a single instance)

    You must decide one of two actions:
      1. "harness_update" — rewrite the scaffold to fix systemic issues
         (parsing bugs, missing tools, bad retry logic, poor prompting strategy).
         Return a JSON object: {"action": "harness_update", "new_scaffold": "<full Python source>",
                                "report": "<prose analysis of changes>"}
      2. "weight_update"  — trigger RL training on the current rollouts when the harness
         has plateaued and domain-specific model knowledge is the bottleneck.
         Choose the most appropriate algorithm from:
           ppo_gae       — dense step-level rewards, stability critical
           grpo          — cheap rollouts, episode-end verifier
           entropic      — sparse/right-skewed rewards
           reinforce_kl  — dense reward, capability regression risk
           best_of_n     — near-zero pass rate, cold-start needed
           dpo           — ordinal ranking possible, no cardinal reward
         Return a JSON object: {"action": "weight_update", "algorithm": "<name>",
                                "report": "<rationale>"}

    Output ONLY a valid JSON object — no prose, no markdown fences.
""").strip()

_FB_USER_TMPL = textwrap.dedent("""
    ## Current scaffold (Ag)
    ```python
    {scaffold}
    ```

    ## Performance metrics (Eg)
    {metrics}

    ## Execution trajectory summary (τg — last {n_examples} instances)
    {trajectory_summary}

    ## Task specification (U)
    {task_spec}

    ## Sample task descriptions (for regularisation)
    {sample_descriptions}

    Select the next action.
""").strip()


@dataclass
class FeedbackDecision:
    action: str  # "harness_update" | "weight_update"
    new_scaffold: str | None = None
    algorithm: str | None = None
    report: str = ""
    raw: str = ""


class FeedbackAgent:
    """Implements the Feedback-Agent decision loop."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        max_tokens: int = 8192,
        trajectory_examples: int = 5,
    ):
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_tokens = max_tokens
        self.trajectory_examples = trajectory_examples

    def decide(
        self,
        scaffold: str,
        trajectory: Trajectory,
        task_spec: str,
        sample_descriptions: list[str] | None = None,
    ) -> FeedbackDecision:
        """Return a FeedbackDecision given the current generation's artefacts."""
        metrics_text = json.dumps(trajectory.metrics, indent=2)
        trajectory_summary = _summarise_trajectory(trajectory, self.trajectory_examples)
        samples_text = "\n".join(sample_descriptions or []) or "(none)"

        user_msg = _FB_USER_TMPL.format(
            scaffold=scaffold,
            metrics=metrics_text,
            n_examples=self.trajectory_examples,
            trajectory_summary=trajectory_summary,
            task_spec=task_spec,
            sample_descriptions=samples_text,
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=_FB_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = response.content[0].text.strip()
        return _parse_decision(raw)

    def get_algorithm(self, name: str) -> WeightUpdateAlgorithm:
        cls = ALGORITHM_REGISTRY.get(name)
        if cls is None:
            raise ValueError(f"Unknown weight-update algorithm: {name!r}. "
                             f"Valid options: {list(ALGORITHM_REGISTRY)}")
        return cls()


def _summarise_trajectory(traj: Trajectory, n: int) -> str:
    lines = []
    for step in traj.steps[-n:]:
        lines.append(
            f"instance={step.instance_id!r} "
            f"reward={step.reward} "
            f"answer={step.extracted_answer!r}\n"
            f"  response_snippet={step.response[:200]!r}"
        )
        if step.tool_calls:
            for tc in step.tool_calls[:2]:
                lines.append(f"  tool={tc.tool!r} error={tc.error!r}")
    return "\n".join(lines) if lines else "(no steps)"


def _parse_decision(raw: str) -> FeedbackDecision:
    try:
        data: dict[str, Any] = json.loads(raw)
        action = data.get("action", "")
        report = data.get("report", "")
        if action == "harness_update":
            return FeedbackDecision(
                action="harness_update",
                new_scaffold=data.get("new_scaffold", ""),
                report=report,
                raw=raw,
            )
        elif action == "weight_update":
            return FeedbackDecision(
                action="weight_update",
                algorithm=data.get("algorithm", "grpo"),
                report=report,
                raw=raw,
            )
        else:
            return FeedbackDecision(action="harness_update", report=f"Unparseable action: {action}", raw=raw)
    except json.JSONDecodeError:
        return FeedbackDecision(action="harness_update", report="JSON parse error", raw=raw)
