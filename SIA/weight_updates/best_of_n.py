"""Best-of-N Behavioural Cloning (cold-start).

Observed when: reward is so sparse that E[r] ≈ 0 across all rollouts and
policy gradient signal is numerically zero.

The Feedback-Agent invokes this as a phase-zero cold-start: the top-k
rollouts by verifier score are distilled into the model via cross-entropy
loss, raising the baseline pass rate to a level where a subsequent PPO or
GRPO phase becomes viable. (§7.3)
"""
from __future__ import annotations

from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class BestOfNBC(WeightUpdateAlgorithm):
    """Best-of-N behavioural cloning for cold-start on sparse rewards."""

    name = "best_of_n"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        top_k: int = 4,
        min_reward_threshold: float = 0.0,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.top_k = top_k
        self.min_reward_threshold = min_reward_threshold

    def _select_demonstrations(self, rollouts: list[Rollout]) -> list[Rollout]:
        """Return the top-k rollouts by reward, filtered by threshold."""
        filtered = [r for r in rollouts if r.reward > self.min_reward_threshold]
        if not filtered:
            filtered = rollouts
        return sorted(filtered, key=lambda r: r.reward, reverse=True)[: self.top_k]

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        mean_reward_before = sum(r.reward for r in rollouts) / max(len(rollouts), 1)
        demonstrations = self._select_demonstrations(rollouts)

        # Cross-entropy (behavioural cloning) loss over selected demonstrations
        total_loss = 0.0
        for demo in demonstrations:
            # -log π(a|s) for the demonstration action
            total_loss += -demo.reward  # placeholder: actual cross-entropy loss

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "n_demonstrations": len(demonstrations),
                "top_k": self.top_k,
                "demo_rewards": [d.reward for d in demonstrations],
            },
        )

    def select_when(self) -> str:
        return (
            "Reward is so sparse that E[r] ≈ 0 across all rollouts and policy gradient "
            "signal is numerically zero. Used as a phase-zero cold-start before PPO/GRPO."
        )
