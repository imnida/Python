"""SIA: Self-Improving AI with Harness & Weight Updates.

A configurable loop in which a language-model agent (the Feedback-Agent)
updates both the harness and the weights of a task-specific agent.

Reference: Hebbar et al., 2026. arXiv:2605.27276

Quick start
-----------
from SIA import SIA
from SIA.tasks import LawBenchTask

task = LawBenchTask()
sia = SIA(
    task_spec=task.task_spec,
    dataset=task.sample_instances(),
    verifier=task.verifier,
    g_max=5,
    reference_impls=task.reference_impl,
)
result = sia.run()
print(f"Best mean reward: {result.best_mean_reward:.4f}")
"""
from .sia_loop import SIA, SIAResult, GenerationRecord
from .meta_agent import MetaAgent
from .feedback_agent import FeedbackAgent
from .task_agent import TaskAgent
from .trajectory import Trajectory, Step, ToolCall
from .verifier import Verifier, ExactMatchVerifier, FunctionVerifier

__all__ = [
    "SIA",
    "SIAResult",
    "GenerationRecord",
    "MetaAgent",
    "FeedbackAgent",
    "TaskAgent",
    "Trajectory",
    "Step",
    "ToolCall",
    "Verifier",
    "ExactMatchVerifier",
    "FunctionVerifier",
]
