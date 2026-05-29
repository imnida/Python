"""Task-Specific Agent: executes a scaffold Ag against a dataset D.

The scaffold is loaded from source, and each instance is run inside a
sandboxed execution environment.  Results are collected into a Trajectory.
"""
from __future__ import annotations

import importlib
import sys
import textwrap
import traceback
import types
from pathlib import Path
from typing import Any, Callable

from .trajectory import Step, Trajectory, ToolCall
from .verifier import Verifier


class TaskAgent:
    """Loads a scaffold from source and runs it against dataset instances."""

    def __init__(self, scaffold_source: str, verifier: Verifier | None = None):
        self.scaffold_source = scaffold_source
        self.verifier = verifier
        self._module: types.ModuleType | None = None

    def _load_module(self) -> types.ModuleType:
        """Compile and load the scaffold source into a fresh module."""
        mod = types.ModuleType("_sia_scaffold")
        mod.__dict__["__builtins__"] = __builtins__
        exec(compile(self.scaffold_source, "<scaffold>", "exec"), mod.__dict__)  # noqa: S102
        return mod

    def run_instance(self, instance: dict[str, Any]) -> Step:
        """Run one dataset instance and return a populated Step."""
        if self._module is None:
            self._module = self._load_module()

        run_fn: Callable = getattr(self._module, "run", None)
        if run_fn is None:
            raise AttributeError("Scaffold has no 'run(instance)' function.")

        try:
            result = run_fn(instance)
            answer = result.get("answer")
            tool_calls = [
                ToolCall(**tc) if isinstance(tc, dict) else tc
                for tc in result.get("tool_calls", [])
            ]
            step = Step(
                instance_id=str(instance.get("id", hash(str(instance)))),
                prompt=result.get("prompt", ""),
                response=result.get("response", ""),
                tool_calls=tool_calls,
                extracted_answer=answer,
            )
        except Exception:
            tb = traceback.format_exc()
            step = Step(
                instance_id=str(instance.get("id", hash(str(instance)))),
                prompt="",
                response="",
                extracted_answer=None,
            )
            step.response = f"<ERROR>\n{tb}"

        if self.verifier is not None:
            ground_truth = instance.get("ground_truth")
            try:
                step.reward = self.verifier.score(step.extracted_answer, ground_truth)
            except Exception:
                step.reward = 0.0

        return step

    def run_dataset(
        self,
        dataset: list[dict[str, Any]],
        generation: int = 0,
    ) -> Trajectory:
        """Run all instances and return the full trajectory τg."""
        # Reload module for each generation to pick up a fresh scaffold.
        self._module = self._load_module()
        traj = Trajectory(generation=generation)
        for instance in dataset:
            step = self.run_instance(instance)
            traj.add_step(step)
        traj.compute_metrics()
        return traj
