"""Entropic Advantage Weighting.

Observed when: the reward histogram is heavily right-skewed — tasks where
correct solutions are rare but individually high-signal, such as hard
mathematical proofs or low-pass-rate code synthesis.

Rather than zeroing out below-average rollouts, gradient mass is
redistributed via softmax with adaptive temperature β:
  wi ∝ exp(ri / β)
The temperature is tuned online so that the effective sample size (ESS)
stays above a floor threshold, preventing collapse onto a single trajectory.
(§7.3; Yuksekgonul et al., 2026)
"""
from __future__ import annotations

import math
from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class EntropicAdvantageWeighting(WeightUpdateAlgorithm):
    """Entropic advantage weighting with adaptive temperature."""

    name = "entropic"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        beta_init: float = 1.0,
        ess_floor: float = 0.2,
        beta_min: float = 0.01,
        beta_max: float = 10.0,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.beta = beta_init
        self.ess_floor = ess_floor
        self.beta_min = beta_min
        self.beta_max = beta_max

    def _softmax_weights(self, rewards: list[float], beta: float) -> list[float]:
        """wi ∝ exp(ri / β), normalised."""
        scaled = [r / beta for r in rewards]
        max_s = max(scaled)
        exp_vals = [math.exp(s - max_s) for s in scaled]
        total = sum(exp_vals)
        return [e / total for e in exp_vals]

    def _effective_sample_size(self, weights: list[float]) -> float:
        """ESS = (Σwi)² / Σwi² — normalised to [0, 1]."""
        n = len(weights)
        sum_sq = sum(w ** 2 for w in weights)
        return 1.0 / (n * sum_sq) if sum_sq > 0 else 1.0

    def _adapt_beta(self, rewards: list[float]) -> float:
        """Tune β so that ESS ≥ ess_floor."""
        beta = self.beta
        for _ in range(20):
            weights = self._softmax_weights(rewards, beta)
            ess = self._effective_sample_size(weights)
            if ess >= self.ess_floor:
                break
            beta = min(beta * 1.5, self.beta_max)
        self.beta = max(self.beta_min, min(beta, self.beta_max))
        return self.beta

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        rewards = [r.reward for r in rollouts]
        mean_reward_before = sum(rewards) / max(len(rewards), 1)

        beta = self._adapt_beta(rewards)
        weights = self._softmax_weights(rewards, beta)

        total_loss = 0.0
        for rollout, w in zip(rollouts, weights):
            # Weighted policy gradient: -w * log π(a|s)
            total_loss += -w  # placeholder: multiply by actual log-prob

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "beta": beta,
                "ess": self._effective_sample_size(weights),
            },
        )

    def select_when(self) -> str:
        return (
            "The reward histogram is heavily right-skewed — tasks where correct solutions "
            "are rare but individually high-signal, such as hard mathematical proofs or "
            "low-pass-rate code synthesis."
        )
