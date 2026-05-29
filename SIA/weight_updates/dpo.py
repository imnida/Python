"""Direct Preference Optimisation (DPO).

Observed when: the verifier can rank outputs but not score them absolutely —
tasks with soft quality criteria where ordinal signal is reliable but
cardinal reward is not.

Given a winning rollout y⁺ and a losing rollout y⁻, the objective
  -log σ(β log πθ(y⁺)/πθ₀(y⁺) − β log πθ(y⁻)/πθ₀(y⁻))
is minimised directly without a reward model. (§7.3)
"""
from __future__ import annotations

import math
from typing import Any

from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout


class PreferencePair:
    """A (winner, loser) pair derived from rollout ranking."""

    def __init__(self, winner: Rollout, loser: Rollout):
        self.winner = winner
        self.loser = loser


class DPO(WeightUpdateAlgorithm):
    """DPO weight update from ranked rollout pairs."""

    name = "dpo"

    def __init__(
        self,
        lora_rank: int = 32,
        learning_rate: float = 4e-5,
        beta: float = 0.1,
        **kwargs: Any,
    ):
        super().__init__(lora_rank=lora_rank, learning_rate=learning_rate, **kwargs)
        self.beta = beta

    def _build_pairs(self, rollouts: list[Rollout]) -> list[PreferencePair]:
        """Sort rollouts by reward and construct (winner, loser) pairs."""
        sorted_rollouts = sorted(rollouts, key=lambda r: r.reward, reverse=True)
        pairs = []
        mid = len(sorted_rollouts) // 2
        for w, l in zip(sorted_rollouts[:mid], sorted_rollouts[mid:]):
            if w.reward > l.reward:
                pairs.append(PreferencePair(winner=w, loser=l))
        return pairs

    def _dpo_loss(self, log_ratio_winner: float, log_ratio_loser: float) -> float:
        """−log σ(β (log πθ(y⁺)/πθ₀(y⁺) − log πθ(y⁻)/πθ₀(y⁻)))."""
        margin = self.beta * (log_ratio_winner - log_ratio_loser)
        # σ(x) = 1 / (1 + exp(-x))
        return math.log(1.0 + math.exp(-margin))

    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        mean_reward_before = sum(r.reward for r in rollouts) / max(len(rollouts), 1)
        pairs = self._build_pairs(rollouts)

        total_loss = 0.0
        for pair in pairs:
            # Placeholder log-ratios (actual implementation needs model forward passes)
            log_ratio_w = pair.winner.log_prob or 0.0
            log_ratio_l = pair.loser.log_prob or 0.0
            total_loss += self._dpo_loss(log_ratio_w, log_ratio_l)

        return WeightUpdateResult(
            algorithm=self.name,
            n_rollouts=len(rollouts),
            mean_reward_before=mean_reward_before,
            mean_reward_after=None,
            loss=total_loss,
            adapter_path=output_path,
            metadata={
                "beta": self.beta,
                "n_pairs": len(pairs),
            },
        )

    def select_when(self) -> str:
        return (
            "The verifier can rank outputs but not score them absolutely — tasks with "
            "soft quality criteria where ordinal signal is reliable but cardinal reward is not."
        )
