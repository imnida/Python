"""PPO with Generalised Advantage Estimation (GAE).

Observed when: step-level rewards are dense and training stability is the
binding constraint — multi-step tool-use or long code-generation tasks where
a single catastrophic update would collapse the policy.

A learned value head Vϕ produces per-token advantage estimates
Ât = Σ_l (γλ)^l δ_{t+l}; a clipped surrogate
min(r_t Ât, clip(r_t, 1±ε) Ât) prevents the policy from leaving the trust
region. (§7.3)
"""
from __future__ import annotations

import math
from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class PPOWithGAE(WeightUpdateAlgorithm):
    """PPO + GAE weight update."""

    name = "ppo_gae"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        clip_epsilon: float = 0.2,
        gamma: float = 0.99,
        lam: float = 0.95,
        n_epochs: int = 4,
        minibatch_size: int = 8,
        value_coef: float = 0.5,
        entropy_coef: float = 0.01,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.clip_epsilon = clip_epsilon
        self.gamma = gamma
        self.lam = lam
        self.n_epochs = n_epochs
        self.minibatch_size = minibatch_size
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef

    def _compute_gae(self, rollouts: list[Rollout]) -> list[float]:
        """Compute GAE advantages Ât = Σ_l (γλ)^l δ_{t+l}."""
        advantages = []
        gae = 0.0
        for rollout in reversed(rollouts):
            v = rollout.value if rollout.value is not None else 0.0
            delta = rollout.reward - v
            gae = delta + self.gamma * self.lam * gae
            advantages.insert(0, gae)
        return advantages

    def _clip_surrogate_loss(self, ratio: float, advantage: float) -> float:
        """min(r_t Ât, clip(r_t, 1±ε) Ât)."""
        clipped = max(1 - self.clip_epsilon, min(1 + self.clip_epsilon, ratio))
        return min(ratio * advantage, clipped * advantage)

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        mean_reward_before = sum(r.reward for r in rollouts) / max(len(rollouts), 1)
        advantages = self._compute_gae(rollouts)

        # Normalise advantages
        mean_adv = sum(advantages) / len(advantages)
        std_adv = math.sqrt(sum((a - mean_adv) ** 2 for a in advantages) / len(advantages)) + 1e-8
        advantages = [(a - mean_adv) / std_adv for a in advantages]

        total_loss = 0.0
        for epoch in range(self.n_epochs):
            for i in range(0, len(rollouts), self.minibatch_size):
                batch = list(zip(rollouts[i:i + self.minibatch_size], advantages[i:i + self.minibatch_size]))
                for rollout, adv in batch:
                    ratio = 1.0  # placeholder: exp(log_prob_new - log_prob_old)
                    policy_loss = -self._clip_surrogate_loss(ratio, adv)
                    value_loss = (rollout.reward - (rollout.value or 0.0)) ** 2
                    total_loss += policy_loss + self.value_coef * value_loss

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "clip_epsilon": self.clip_epsilon,
                "gamma": self.gamma,
                "lam": self.lam,
                "n_epochs": self.n_epochs,
            },
        )

    def select_when(self) -> str:
        return (
            "Step-level rewards are dense and training stability is the binding constraint; "
            "multi-step tool-use or long code-generation tasks where a single catastrophic "
            "update would collapse the policy."
        )
