#!/usr/bin/env python3
"""
Agent Workflow Automation using the Claude API.

Routes a task description to the correct engineering workflow from the
agent-workflows library and executes it via a multi-turn conversation
with Claude Opus 4.8. Uses streaming and prompt caching to reduce cost.

Usage:
    python agent_workflow.py                          # interactive CLI
    python agent_workflow.py "fix the login bug"      # single-shot CLI
    python agent_workflow.py --workflow bug-fix "..."  # force a workflow

Programmatic:
    from agent_workflow import AgentWorkflowRunner
    runner = AgentWorkflowRunner()
    runner.run("describe the task here")
"""

from __future__ import annotations

import argparse
import sys
from typing import Iterator

import anthropic

from workflow_router import WorkflowLibrary, load_library, list_workflows

MODEL = "claude-opus-4-8"

CLASSIFIER_SYSTEM = """\
You are a workflow router for an engineering agent. Your job is to classify \
a user task into exactly one of these workflow categories:

- project-initialization
- feature
- bug-fix
- code-review
- incident
- refactoring
- tech-debt

Respond with ONLY the category name — no explanation, no punctuation, just \
the bare category string.

If the task is ambiguous but low-risk, pick the most likely category and \
output just that category. If the task is genuinely unclear, output:
  ask: <one short clarifying question>
"""

EXECUTOR_SYSTEM_TEMPLATE = """\
You are an expert engineering agent that executes structured workflows.

You have access to the agent-workflows library, which defines reusable \
engineering processes for common development tasks.

Follow the loaded workflow exactly — run preflight, triage gate, and only \
the steps required by the triage result. Apply all safety rules. When the \
workflow requests validation commands, describe them clearly. End with the \
workflow's handoff format.

Do not commit or push code unless the user explicitly approves.

{shared_context}
"""


class AgentWorkflowRunner:
    """Route and execute engineering workflows using Claude Opus 4.8."""

    def __init__(self, library: WorkflowLibrary | None = None) -> None:
        self.client = anthropic.Anthropic()
        self.lib = library or load_library()
        self._shared_ctx = self.lib.shared_context()

    # ------------------------------------------------------------------
    # Classification
    # ------------------------------------------------------------------

    def classify(self, task: str) -> str:
        """
        Ask Claude to classify the task into a workflow category.
        Returns the category name, or raises ValueError with a clarifying
        question if the task is too ambiguous.
        """
        response = self.client.messages.create(
            model=MODEL,
            max_tokens=64,
            system=CLASSIFIER_SYSTEM,
            messages=[{"role": "user", "content": task}],
        )
        raw = next(
            (b.text.strip() for b in response.content if b.type == "text"), ""
        )

        if raw.startswith("ask:"):
            question = raw[4:].strip()
            raise ValueError(question)

        if raw not in list_workflows():
            # Best-effort fuzzy fallback
            for wf in list_workflows():
                if wf in raw or raw in wf:
                    return wf
            raise ValueError(
                f"Claude returned an unrecognised workflow: {raw!r}. "
                f"Valid values: {list_workflows()}"
            )
        return raw

    # ------------------------------------------------------------------
    # Execution helpers
    # ------------------------------------------------------------------

    def _build_system(self) -> list[dict]:
        """Return a cached system prompt block."""
        text = EXECUTOR_SYSTEM_TEMPLATE.format(shared_context=self._shared_ctx)
        return [{"type": "text", "text": text, "cache_control": {"type": "ephemeral"}}]

    def _stream_response(
        self,
        messages: list[dict],
        extra_content: list[dict] | None = None,
    ) -> tuple[str, list]:
        """
        Send a streaming request and return (full_text, full_content_blocks).
        `extra_content` is prepended as cached content in the last user turn.
        """
        if extra_content:
            # Inject cached workflow doc into the last user message
            last = messages[-1]
            if last["role"] == "user":
                existing = last["content"]
                if isinstance(existing, str):
                    existing = [{"type": "text", "text": existing}]
                messages = messages[:-1] + [
                    {"role": "user", "content": extra_content + list(existing)}
                ]

        text_parts: list[str] = []
        with self.client.messages.stream(
            model=MODEL,
            max_tokens=16000,
            thinking={"type": "adaptive"},
            system=self._build_system(),
            messages=messages,
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta":
                    if event.delta.type == "text_delta":
                        chunk = event.delta.text
                        text_parts.append(chunk)
                        print(chunk, end="", flush=True)

            final = stream.get_final_message()

        print()  # newline after streaming ends
        full_text = "".join(text_parts)
        return full_text, list(final.content)

    # ------------------------------------------------------------------
    # Workflow execution
    # ------------------------------------------------------------------

    def _workflow_content_block(self, workflow_name: str) -> list[dict]:
        """Return a cached content block containing the workflow doc."""
        doc = self.lib.workflow_context(workflow_name)
        return [
            {
                "type": "text",
                "text": (
                    f"## Loaded Workflow: {workflow_name}\n\n"
                    "Apply this workflow now. Run the preflight and triage "
                    "gate first, then follow only the steps required.\n\n"
                    f"{doc}"
                ),
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def run(
        self,
        task: str,
        workflow: str | None = None,
        interactive: bool = True,
    ) -> None:
        """
        Classify and execute the workflow for `task`.

        Args:
            task: The user's task description.
            workflow: Force a specific workflow (skip classification).
            interactive: Whether to continue the conversation after first response.
        """
        # 1. Classify
        if workflow:
            wf_name = workflow
            print(f"\n[Workflow forced: {wf_name}]\n")
        else:
            print("\n[Classifying task...]")
            try:
                wf_name = self.classify(task)
            except ValueError as question:
                print(f"\nClarification needed: {question}")
                if interactive:
                    answer = input("Your answer: ").strip()
                    task = f"{task}\n\nClarification: {answer}"
                    wf_name = self.classify(task)
                else:
                    raise
            print(f"[Selected workflow: {wf_name}]\n")

        # 2. Build cached workflow doc as prepended content
        workflow_blocks = self._workflow_content_block(wf_name)

        # 3. First turn — task + workflow doc (cached)
        messages: list[dict] = [
            {"role": "user", "content": task}
        ]

        print(f"{'─' * 60}")
        print(f"  Executing: {wf_name} workflow")
        print(f"{'─' * 60}\n")

        _, content_blocks = self._stream_response(messages, extra_content=workflow_blocks)

        # Append assistant response to history
        messages.append({"role": "assistant", "content": content_blocks})

        if not interactive:
            return

        # 4. Multi-turn follow-up
        print(f"\n{'─' * 60}")
        print("  Continue the workflow (type 'done' to exit)")
        print(f"{'─' * 60}")

        while True:
            try:
                user_input = input("\nYou: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[Session ended]")
                break

            if not user_input or user_input.lower() in {"done", "exit", "quit", "q"}:
                print("[Workflow session complete]")
                break

            messages.append({"role": "user", "content": user_input})
            _, content_blocks = self._stream_response(messages)
            messages.append({"role": "assistant", "content": content_blocks})


# ------------------------------------------------------------------
# CLI entry point
# ------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Route and execute engineering workflows using Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="\n".join([
            "Examples:",
            "  python agent_workflow.py                       # interactive",
            '  python agent_workflow.py "fix the login bug"  # single task',
            '  python agent_workflow.py --workflow bug-fix "login fails on mobile"',
            '  python agent_workflow.py --no-interactive "review PR #42"',
        ]),
    )
    parser.add_argument(
        "task",
        nargs="?",
        default=None,
        help="Task description. Omit to enter interactively.",
    )
    parser.add_argument(
        "--workflow",
        choices=list_workflows(),
        default=None,
        help="Force a specific workflow (skip classification).",
    )
    parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Run one turn and exit (no follow-up prompts).",
    )
    parser.add_argument(
        "--list-workflows",
        action="store_true",
        help="Print available workflow names and exit.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if args.list_workflows:
        for wf in list_workflows():
            print(wf)
        return 0

    try:
        runner = AgentWorkflowRunner()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    task = args.task
    if not task:
        print("Agent Workflow Runner — powered by Claude Opus 4.8")
        print("Enter your task description (or 'quit' to exit):\n")
        try:
            task = input("Task: ").strip()
        except (EOFError, KeyboardInterrupt):
            return 0
        if not task or task.lower() in {"quit", "exit", "q"}:
            return 0

    try:
        runner.run(
            task=task,
            workflow=args.workflow,
            interactive=not args.no_interactive,
        )
    except KeyboardInterrupt:
        print("\n[Interrupted]")
    except anthropic.APIError as exc:
        print(f"\nAPI error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
