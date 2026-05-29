"""SIA configurable loop — the top-level orchestrator.

Architecture (§5.1, Figure 3):
  1. Meta-Agent M initialises A1 from task spec U and reference impls R.
  2. For each generation g up to G_max:
     a. Execute: run Ag against D, capture trajectory τg.
     b. Feedback-Agent F analyses (Ag, τg, Eg, U) and selects an action:
        - harness_update → Ag+1 = F(Ag, τg, Eg, U), weights fixed.
        - weight_update  → RL training step on rollouts from τg, scaffold fixed.
  3. Return the best scaffold and LoRA checkpoint found.
"""
from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .feedback_agent import FeedbackAgent, FeedbackDecision
from .meta_agent import MetaAgent
from .task_agent import TaskAgent
from .trajectory import Trajectory
from .verifier import Verifier
from .weight_updates import Rollout, WeightUpdateResult

logger = logging.getLogger(__name__)


@dataclass
class GenerationRecord:
    """Snapshot of one generation."""
    generation: int
    action: str  # "harness_update" | "weight_update"
    scaffold: str
    trajectory: Trajectory
    feedback_report: str
    weight_update_result: WeightUpdateResult | None = None
    mean_reward: float = 0.0
    elapsed_sec: float = 0.0


@dataclass
class SIAResult:
    """Final result returned by SIA.run()."""
    best_scaffold: str
    best_mean_reward: float
    generations: list[GenerationRecord] = field(default_factory=list)
    adapter_path: str | None = None
    base_model_id: str = ""


class SIA:
    """Self-Improving AI loop.

    Parameters
    ----------
    task_spec:
        Human-readable description of the task (benchmark name, input/output
        format, metric definition).  Passed verbatim to the Meta-Agent and
        Feedback-Agent.
    dataset:
        List of instance dicts.  Each instance must contain at least an "id"
        and a "ground_truth" key (consumed by the verifier).
    verifier:
        Deterministic verifier V that scores each model answer.
    g_max:
        Maximum number of SIA loop iterations (harness or weight updates).
    base_model_id:
        Identifier for the task-specific LLM (e.g. "openai/gpt-oss-120b").
    reference_impls:
        Optional reference implementations to seed the Meta-Agent.
    sample_descriptions:
        Diverse task descriptions for sample-task regularisation (§5.3).
    output_dir:
        Directory to write scaffold source and LoRA adapter checkpoints.
    stall_patience:
        Number of consecutive non-improving harness steps before the
        Feedback-Agent is forced to consider a weight update.
    """

    def __init__(
        self,
        task_spec: str,
        dataset: list[dict[str, Any]],
        verifier: Verifier,
        g_max: int = 10,
        base_model_id: str = "openai/gpt-oss-120b",
        reference_impls: str = "",
        sample_descriptions: list[str] | None = None,
        output_dir: str = "sia_output",
        stall_patience: int = 3,
    ):
        self.task_spec = task_spec
        self.dataset = dataset
        self.verifier = verifier
        self.g_max = g_max
        self.base_model_id = base_model_id
        self.reference_impls = reference_impls
        self.sample_descriptions = sample_descriptions or []
        self.output_dir = Path(output_dir)
        self.stall_patience = stall_patience

        self._meta_agent = MetaAgent()
        self._feedback_agent = FeedbackAgent()

    def run(self) -> SIAResult:
        """Execute the SIA loop and return the best scaffold + adapter."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # ── Generation 0: initialise scaffold from Meta-Agent ──────────────
        logger.info("Meta-Agent generating initial scaffold A1 …")
        scaffold = self._meta_agent.generate_scaffold(
            task_spec=self.task_spec,
            reference_impls=self.reference_impls,
            sample_instances=self.dataset[:5] if self.dataset else [],
        )
        self._save_scaffold(scaffold, generation=1)

        records: list[GenerationRecord] = []
        best_scaffold = scaffold
        best_reward = 0.0
        adapter_path: str | None = None
        stall_count = 0

        for g in range(1, self.g_max + 1):
            t0 = time.time()
            logger.info("Generation %d — executing scaffold …", g)

            # ── Execution phase ──────────────────────────────────────────────
            agent = TaskAgent(scaffold_source=scaffold, verifier=self.verifier)
            trajectory = agent.run_dataset(self.dataset, generation=g)
            mean_reward = trajectory.metrics.get("mean_reward", 0.0)
            logger.info("Generation %d — mean_reward=%.4f", g, mean_reward)

            if mean_reward > best_reward:
                best_reward = mean_reward
                best_scaffold = scaffold
                stall_count = 0
            else:
                stall_count += 1

            # ── Analysis + Improvement phase ─────────────────────────────────
            decision: FeedbackDecision = self._feedback_agent.decide(
                scaffold=scaffold,
                trajectory=trajectory,
                task_spec=self.task_spec,
                sample_descriptions=self.sample_descriptions,
            )
            logger.info("Generation %d — Feedback-Agent chose: %s", g, decision.action)

            wu_result: WeightUpdateResult | None = None

            if decision.action == "harness_update" and decision.new_scaffold:
                scaffold = decision.new_scaffold
                self._save_scaffold(scaffold, generation=g + 1)

            elif decision.action == "weight_update" and decision.algorithm:
                algorithm_name = decision.algorithm
                wu = self._feedback_agent.get_algorithm(algorithm_name)
                rollouts = _trajectory_to_rollouts(trajectory)
                out_path = str(self.output_dir / f"adapter_g{g}")
                wu_result = wu.train(
                    rollouts=rollouts,
                    base_model_id=self.base_model_id,
                    adapter_path=adapter_path,
                    output_path=out_path,
                )
                adapter_path = wu_result.adapter_path
                logger.info(
                    "Generation %d — weight update (%s) loss=%.4f",
                    g,
                    algorithm_name,
                    wu_result.loss or 0.0,
                )
            else:
                # Fallback: treat as harness update with unchanged scaffold
                logger.warning("Generation %d — unrecognised action %r, keeping scaffold.", g, decision.action)

            records.append(GenerationRecord(
                generation=g,
                action=decision.action,
                scaffold=scaffold,
                trajectory=trajectory,
                feedback_report=decision.report,
                weight_update_result=wu_result,
                mean_reward=mean_reward,
                elapsed_sec=time.time() - t0,
            ))

            if stall_count >= self.stall_patience and g < self.g_max:
                logger.info(
                    "Harness stalled for %d consecutive steps (generation %d). "
                    "Feedback-Agent will be nudged toward weight update.",
                    stall_count, g,
                )

        return SIAResult(
            best_scaffold=best_scaffold,
            best_mean_reward=best_reward,
            generations=records,
            adapter_path=adapter_path,
            base_model_id=self.base_model_id,
        )

    def _save_scaffold(self, source: str, generation: int) -> None:
        path = self.output_dir / f"scaffold_g{generation}.py"
        path.write_text(source, encoding="utf-8")
        logger.debug("Saved scaffold to %s", path)


def _trajectory_to_rollouts(trajectory: Trajectory) -> list[Rollout]:
    """Convert trajectory steps to Rollout objects for weight-update algorithms."""
    return [
        Rollout(
            state=step.prompt,
            action=step.response,
            reward=step.reward if step.reward is not None else 0.0,
        )
        for step in trajectory.steps
    ]
