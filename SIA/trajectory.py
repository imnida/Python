"""Trajectory capture and logging for the SIA loop."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ToolCall:
    tool: str
    args: dict[str, Any]
    result: Any
    error: str | None = None


@dataclass
class Step:
    instance_id: str
    prompt: str
    response: str
    tool_calls: list[ToolCall] = field(default_factory=list)
    extracted_answer: Any = None
    reward: float | None = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class Trajectory:
    """Full execution log from running a scaffold Ag against dataset D."""
    generation: int
    steps: list[Step] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    error_log: list[str] = field(default_factory=list)

    def add_step(self, step: Step) -> None:
        self.steps.append(step)

    def compute_metrics(self) -> dict[str, Any]:
        rewards = [s.reward for s in self.steps if s.reward is not None]
        if not rewards:
            return {}
        self.metrics = {
            "n_instances": len(self.steps),
            "n_scored": len(rewards),
            "mean_reward": sum(rewards) / len(rewards),
            "pass_rate": sum(1 for r in rewards if r > 0) / len(rewards),
            "rewards": rewards,
        }
        return self.metrics

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Trajectory":
        steps = [
            Step(
                instance_id=s["instance_id"],
                prompt=s["prompt"],
                response=s["response"],
                tool_calls=[ToolCall(**tc) for tc in s.get("tool_calls", [])],
                extracted_answer=s.get("extracted_answer"),
                reward=s.get("reward"),
                timestamp=s.get("timestamp", 0.0),
            )
            for s in d.get("steps", [])
        ]
        t = cls(generation=d["generation"], steps=steps, metrics=d.get("metrics", {}), error_log=d.get("error_log", []))
        return t
