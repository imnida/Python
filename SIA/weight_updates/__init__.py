"""Weight update algorithms selected dynamically by the Feedback-Agent."""
from .base import WeightUpdateAlgorithm, WeightUpdateResult, Rollout
from .ppo_gae import PPOWithGAE
from .grpo import GRPO
from .entropic import EntropicAdvantageWeighting
from .reinforce_kl import REINFORCEWithKL
from .best_of_n import BestOfNBC
from .dpo import DPO

__all__ = [
    "WeightUpdateAlgorithm",
    "WeightUpdateResult",
    "Rollout",
    "PPOWithGAE",
    "GRPO",
    "EntropicAdvantageWeighting",
    "REINFORCEWithKL",
    "BestOfNBC",
    "DPO",
    "ALGORITHM_REGISTRY",
]

ALGORITHM_REGISTRY: dict[str, type[WeightUpdateAlgorithm]] = {
    "ppo_gae": PPOWithGAE,
    "grpo": GRPO,
    "entropic": EntropicAdvantageWeighting,
    "reinforce_kl": REINFORCEWithKL,
    "best_of_n": BestOfNBC,
    "dpo": DPO,
}
