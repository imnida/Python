"""Group Relative Policy Optimisation (GRPO).

Observed when: rollouts are cheap to sample and the verifier fires at episode
end — classification, short-answer, or unit-test tasks where hundreds of
completions can be scored in a single forward pass.

Advantages are normalised within a rollout group of size G:
Âi = (ri − r̄) / σr, eliminating the value network entirely.
This halves memory and enables large parallel batches. (§7.3)
"""
from __future__ import annotations

import math
from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class GRPO(WeightUpdateAlgorithm):
    """GRPO weight update."""

    name = "grpo"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        group_size: int = 8,
        kl_coef: float = 0.01,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.group_size = group_size
        self.kl_coef = kl_coef

    def _group_advantages(self, rollouts: list[Rollout]) -> list[float]:
        """Normalise rewards within groups of size G: Âi = (ri − r̄) / σr."""
        advantages = []
        for i in range(0, len(rollouts), self.group_size):
            group = rollouts[i:i + self.group_size]
            rewards = [r.reward for r in group]
            mean_r = sum(rewards) / len(rewards)
            std_r = math.sqrt(sum((r - mean_r) ** 2 for r in rewards) / len(rewards)) + 1e-8
            advantages.extend((r - mean_r) / std_r for r in rewards)
        return advantages

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        mean_reward_before = sum(r.reward for r in rollouts) / max(len(rollouts), 1)
        advantages = self._group_advantages(rollouts)

        total_loss = 0.0
        for rollout, adv in zip(rollouts, advantages):
            # Policy gradient loss: -log π(a|s) * Â
            policy_loss = -adv  # placeholder: multiply by actual log-prob
            total_loss += policy_loss

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "group_size": self.group_size,
                "kl_coef": self.kl_coef,
            },
        )

    def select_when(self) -> str:
        return (
            "Rollouts are cheap to sample and the verifier fires at episode end — "
            "classification, short-answer, or unit-test tasks where hundreds of "
            "completions can be scored in a single forward pass."
        )
