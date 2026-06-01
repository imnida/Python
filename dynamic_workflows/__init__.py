"""
dynamic_workflows — Claude-Code-style multi-agent workflow runtime for Python.

Inspired by https://github.com/Michaelliv/pi-dynamic-workflows (TypeScript/Pi).

Quick start:

    from dynamic_workflows import run_workflow, WorkflowMeta, WorkflowRunOptions
    from dynamic_workflows.agent import EchoAgent  # or AnthropicAgent

    meta = WorkflowMeta(name="demo", description="A demo workflow")

    async def my_workflow():
        phase("Scan")
        result = await agent("List the Python files here.", label="scanner")
        return result

    import asyncio
    output = asyncio.run(
        run_workflow(my_workflow, meta, WorkflowRunOptions(agent=EchoAgent()))
    )
    print(output.result)
"""

from .agent import AnthropicAgent, BaseWorkflowAgent, EchoAgent
from .display import (
    NullDisplay,
    PrintDisplay,
    WorkflowDisplay,
    create_text_display,
    render_workflow_lines,
    render_workflow_text,
)
from .runtime import WorkflowRunOptions, run_workflow
from .types import (
    AgentOptions,
    WorkflowAgentSnapshot,
    WorkflowMeta,
    WorkflowMetaPhase,
    WorkflowRunResult,
    WorkflowSnapshot,
)

__all__ = [
    # Runtime
    "run_workflow",
    "WorkflowRunOptions",
    # Agents
    "BaseWorkflowAgent",
    "AnthropicAgent",
    "EchoAgent",
    # Display
    "WorkflowDisplay",
    "NullDisplay",
    "PrintDisplay",
    "create_text_display",
    "render_workflow_lines",
    "render_workflow_text",
    # Types
    "WorkflowMeta",
    "WorkflowMetaPhase",
    "WorkflowRunResult",
    "WorkflowSnapshot",
    "WorkflowAgentSnapshot",
    "AgentOptions",
]
