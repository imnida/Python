from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional


@dataclass
class WorkflowMetaPhase:
    title: str
    detail: Optional[str] = None
    model: Optional[str] = None


@dataclass
class WorkflowMeta:
    name: str
    description: str
    when_to_use: Optional[str] = None
    phases: list[WorkflowMetaPhase] = field(default_factory=list)


WorkflowAgentStatus = Literal["queued", "running", "done", "error", "skipped"]


@dataclass
class WorkflowAgentSnapshot:
    id: int
    label: str
    prompt: str
    status: WorkflowAgentStatus
    phase: Optional[str] = None
    result_preview: Optional[str] = None
    error: Optional[str] = None


@dataclass
class WorkflowSnapshot:
    name: str
    phases: list[str]
    logs: list[str]
    agents: list[WorkflowAgentSnapshot]
    agent_count: int
    running_count: int
    done_count: int
    error_count: int
    description: Optional[str] = None
    current_phase: Optional[str] = None
    duration_ms: Optional[float] = None
    result: Optional[Any] = None


@dataclass
class WorkflowRunResult:
    meta: WorkflowMeta
    result: Any
    logs: list[str]
    phases: list[str]
    agent_count: int
    duration_ms: float


@dataclass
class AgentOptions:
    label: Optional[str] = None
    phase: Optional[str] = None
    schema: Optional[dict] = None
    model: Optional[str] = None
    instructions: Optional[str] = None
