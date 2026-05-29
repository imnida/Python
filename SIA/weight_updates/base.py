"""Base class for weight-update algorithms."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Rollout:
    """A single sampled trajectory from the current policy."""
    state: str
    action: str
    reward: float
    log_prob: float | None = None
    value: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WeightUpdateResult:
    algorithm: str
    n_rollouts: int
    mean_reward_before: float
    mean_reward_after: float | None
    loss: float | None
    adapter_path: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class WeightUpdateAlgorithm(ABC):
    """Abstract base for RL / imitation-learning weight-update algorithms.

    Subclasses implement train(), which adapts a LoRA checkpoint given a
    batch of rollouts and returns a WeightUpdateResult.
    """

    name: str = "base"

    def __init__(self, lora_rank: int = 32, learning_rate: float = 4e-5, **kwargs):
        self.lora_rank = lora_rank
        self.learning_rate = learning_rate
        self.config = kwargs

    @abstractmethod
    def train(
        self,
        rollouts: list[Rollout],
        base_model_id: str,
        adapter_path: str | None = None,
        output_path: str | None = None,
    ) -> WeightUpdateResult:
        """Adapt model weights given rollouts and return the result."""

    def select_when(self) -> str:
        """Human-readable description of when this algorithm is appropriate."""
        return ""
