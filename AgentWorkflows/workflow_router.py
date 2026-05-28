#!/usr/bin/env python3
# Function Name: WorkflowRouter
# Description: Locate the agent-workflows library and load the correct workflow for a task.

from __future__ import annotations

import os
import sys
from pathlib import Path

WORKFLOW_FILES = {
    "project-initialization": "project-initialization-agent-workflow.md",
    "feature": "feature-development-agent-workflow.md",
    "bug-fix": "bug-fix-agent-workflow.md",
    "code-review": "code-review-agent-workflow.md",
    "incident": "incident-debugging-agent-workflow.md",
    "refactoring": "refactoring-agent-workflow.md",
    "tech-debt": "tech-debt-cleanup-agent-workflow.md",
}

SHARED_FILES = {
    "readme": "README.md",
    "preflight": "shared/repository-preflight.md",
    "safety_rules": "shared/safety-rules.md",
    "workflow_conventions": "shared/workflow-conventions.md",
}

ROUTING_GUIDE = """
## Workflow Selection Rules

- project-initialization: New projects, greenfield codebases, initial scaffolding, initial tooling setup
- feature: New capabilities, product behavior changes, new APIs, any task needing design before coding
- bug-fix: Something is broken, incorrect, regressed, or failing; goal is to restore correct behavior
- code-review: User asks for review of code, a PR, a branch, or workspace changes (read-only findings)
- incident: Production/live-environment failures, alerts, outages, data corruption, degraded performance
- refactoring: Structural improvement with NO intended behavior change
- tech-debt: Cleanup, dead code removal, dependency upgrades, TODO/FIXME resolution, debt surveys

## Ambiguity Handling

- Ask one short clarifying question only when the workflow choice would materially change actions taken.
- If ambiguity is low-risk, pick the most likely workflow, state the assumption, and proceed.
- If the user explicitly names a workflow, use it.
"""


def _is_library_root(path: Path) -> bool:
    if not path.is_dir():
        return False
    return (path / "README.md").is_file() and all(
        (path / rel).is_file() for rel in WORKFLOW_FILES.values()
    )


def find_library_root() -> Path | None:
    """Find the agent-workflows library root via env var, then common locations."""
    env_root = os.environ.get("AGENT_WORKFLOWS_ROOT")
    if env_root:
        p = Path(env_root).expanduser().resolve()
        if _is_library_root(p):
            return p

    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / "agent-workflows",
        script_dir.parent / "agent-workflows",
        Path("/tmp/agent-workflows"),
        Path.home() / "agent-workflows",
    ]
    for cwd_part in [Path.cwd(), *Path.cwd().parents]:
        candidates.append(cwd_part / "agent-workflows")
        if cwd_part.name == "agent-workflows":
            candidates.append(cwd_part)

    seen: set[Path] = set()
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        if _is_library_root(resolved):
            return resolved

    return None


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:
        return f"[Error reading {path}: {exc}]"


class WorkflowLibrary:
    """Loaded agent-workflows library ready for use."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._cache: dict[str, str] = {}

    def _get(self, rel: str) -> str:
        if rel not in self._cache:
            self._cache[rel] = _read_file(self.root / rel)
        return self._cache[rel]

    @property
    def readme(self) -> str:
        return self._get("README.md")

    @property
    def preflight(self) -> str:
        return self._get("shared/repository-preflight.md")

    @property
    def safety_rules(self) -> str:
        return self._get("shared/safety-rules.md")

    @property
    def workflow_conventions(self) -> str:
        return self._get("shared/workflow-conventions.md")

    def workflow_doc(self, name: str) -> str:
        """Return the markdown content for a named workflow."""
        if name not in WORKFLOW_FILES:
            raise ValueError(f"Unknown workflow: {name!r}. Valid: {sorted(WORKFLOW_FILES)}")
        return self._get(WORKFLOW_FILES[name])

    def shared_context(self) -> str:
        """Concatenated shared docs used in every workflow system prompt."""
        parts = [
            "# Agent Workflows — Shared Context\n",
            "## Overview\n",
            self.readme,
            "\n---\n## Repository Preflight\n",
            self.preflight,
            "\n---\n## Safety Rules\n",
            self.safety_rules,
            "\n---\n## Workflow Conventions\n",
            self.workflow_conventions,
            "\n---\n## Routing Guide\n",
            ROUTING_GUIDE,
        ]
        return "\n".join(parts)

    def workflow_context(self, name: str) -> str:
        """Full context for executing a specific workflow."""
        return (
            f"# Workflow: {name}\n\n"
            + self.workflow_doc(name)
        )


def load_library() -> WorkflowLibrary:
    """Find and return the workflow library, raising if not found."""
    root = find_library_root()
    if root is None:
        raise RuntimeError(
            "agent-workflows library not found. "
            "Set AGENT_WORKFLOWS_ROOT or place it adjacent to this file."
        )
    return WorkflowLibrary(root)


def list_workflows() -> list[str]:
    return sorted(WORKFLOW_FILES)


if __name__ == "__main__":
    lib = load_library()
    print(f"Library root: {lib.root}")
    print(f"Workflows: {list_workflows()}")
