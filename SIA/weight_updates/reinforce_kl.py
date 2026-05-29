"""REINFORCE + KL-to-base regularisation.

Observed when: the reward is dense and the primary risk is capability
regression rather than gradient variance — fine-grained domain-adaptation
tasks where the base model is already near-capable and large parameter
movement is undesirable.

Monte Carlo returns Rt = Σ_{t'≥t} γ^{t'-t} r_{t'} serve as advantages
directly, augmented with a penalty α KL(πθ ‖ πθ₀) against the frozen
reference. No critic, no grouping — the simplest possible training loop.
(§7.3)
"""
from __future__ import annotations

from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class REINFORCEWithKL(WeightUpdateAlgorithm):
    """REINFORCE with KL penalty to the frozen reference policy."""

    name = "reinforce_kl"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        gamma: float = 0.99,
        kl_coef: float = 0.1,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.gamma = gamma
        self.kl_coef = kl_coef

    def _monte_carlo_returns(self, rollout: Rollout) -> float:
        """Rt = reward for single-step rollout (no multi-step decomposition here)."""
        return rollout.reward

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        mean_reward_before = sum(r.reward for r in rollouts) / max(len(rollouts), 1)

        total_loss = 0.0
        for rollout in rollouts:
            returns = self._monte_carlo_returns(rollout)
            # Policy gradient term: -log π(a|s) * R_t
            pg_loss = -returns  # placeholder: multiply by actual log-prob
            # KL penalty: α * KL(πθ ‖ πθ₀)  — approximated as 0 without actual model
            kl_penalty = self.kl_coef * 0.0
            total_loss += pg_loss + kl_penalty

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "gamma": self.gamma,
                "kl_coef": self.kl_coef,
            },
        )

    def select_when(self) -> str:
        return (
            "The reward is dense and the primary risk is capability regression — "
            "fine-grained domain-adaptation tasks where the base model is already "
            "near-capable and large parameter movement is undesirable."
        )
