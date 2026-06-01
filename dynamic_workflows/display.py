from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Optional

from .types import WorkflowAgentStatus, WorkflowSnapshot


class WorkflowDisplay(ABC):
    @abstractmethod
    def update(self, snapshot: WorkflowSnapshot) -> None: ...

    @abstractmethod
    def complete(self, snapshot: WorkflowSnapshot) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...


class NullDisplay(WorkflowDisplay):
    def update(self, snapshot: WorkflowSnapshot) -> None:
        pass

    def complete(self, snapshot: WorkflowSnapshot) -> None:
        pass

    def clear(self) -> None:
        pass


class PrintDisplay(WorkflowDisplay):
    """Prints workflow progress to stdout."""

    def __init__(self, verbose: bool = False) -> None:
        self._verbose = verbose

    def update(self, snapshot: WorkflowSnapshot) -> None:
        if self._verbose:
            print(render_workflow_text(snapshot, completed=False))

    def complete(self, snapshot: WorkflowSnapshot) -> None:
        print(render_workflow_text(snapshot, completed=True))

    def clear(self) -> None:
        pass


def create_text_display(verbose: bool = False) -> WorkflowDisplay:
    return PrintDisplay(verbose=verbose)


def recompute_snapshot(snapshot: WorkflowSnapshot) -> WorkflowSnapshot:
    running = sum(1 for a in snapshot.agents if a.status == "running")
    done = sum(1 for a in snapshot.agents if a.status == "done")
    errors = sum(1 for a in snapshot.agents if a.status == "error")
    return WorkflowSnapshot(
        name=snapshot.name,
        description=snapshot.description,
        phases=snapshot.phases,
        current_phase=snapshot.current_phase,
        logs=snapshot.logs,
        agents=snapshot.agents,
        agent_count=len(snapshot.agents),
        running_count=running,
        done_count=done,
        error_count=errors,
        duration_ms=snapshot.duration_ms,
        result=snapshot.result,
    )


def render_workflow_lines(
    snapshot: WorkflowSnapshot,
    max_agents: int = 8,
    max_logs: int = 2,
    show_result_previews: bool = False,
) -> list[str]:
    state_str = ""
    if snapshot.error_count > 0:
        state_str = f", {snapshot.error_count} errors"
    elif snapshot.running_count > 0:
        state_str = f", {snapshot.running_count} running"
    lines = [f"◆ Workflow: {snapshot.name} ({snapshot.done_count}/{snapshot.agent_count} done{state_str})"]

    agent_phases = {a.phase for a in snapshot.agents if a.phase}
    phase_names = _unique([*snapshot.phases, *(([snapshot.current_phase]) if snapshot.current_phase else []), *agent_phases])

    rendered: set[int] = set()
    for phase in phase_names:
        phase_agents = [a for a in snapshot.agents if a.phase == phase]
        if not phase_agents and snapshot.current_phase != phase:
            continue
        for a in phase_agents:
            rendered.add(a.id)
        done = sum(1 for a in phase_agents if a.status == "done")
        running = sum(1 for a in phase_agents if a.status == "running")
        errors = sum(1 for a in phase_agents if a.status == "error")
        skipped = sum(1 for a in phase_agents if a.status == "skipped")
        complete = phase_agents and (done + errors + skipped == len(phase_agents))
        if running or (not complete and snapshot.current_phase == phase):
            marker = "▶"
        elif complete:
            marker = "✓"
        else:
            marker = " "
        extra = ""
        if running:
            extra += f" · {running} running"
        if errors:
            extra += f" · {errors} errors"
        if skipped:
            extra += f" · {skipped} skipped"
        lines.append(f"  {marker} {phase} {done}/{len(phase_agents)}{extra}")
        visible = phase_agents[-max_agents:]
        for a in visible:
            result_str = f" — {a.result_preview}" if show_result_previews and a.result_preview else ""
            lines.append(f"    #{a.id} {_status_icon(a.status)} {_shorten(a.label, 48)}{result_str}")
        if len(phase_agents) > len(visible):
            lines.append(f"    … {len(phase_agents) - len(visible)} earlier agents")

    unphased = [a for a in snapshot.agents if a.id not in rendered]
    if unphased:
        lines.append("  Unphased")
        for a in unphased[-max_agents:]:
            result_str = f" — {a.result_preview}" if show_result_previews and a.result_preview else ""
            lines.append(f"    #{a.id} {_status_icon(a.status)} {_shorten(a.label, 48)}{result_str}")

    visible_logs = snapshot.logs[-max_logs:]
    if visible_logs:
        if len(lines) > 1:
            lines.append("")
        for entry in visible_logs:
            lines.append(f"  log: {entry}")

    return lines


def render_workflow_text(snapshot: WorkflowSnapshot, completed: bool = False) -> str:
    header = "Workflow completed" if completed else "Workflow running"
    return "\n".join([header, *render_workflow_lines(snapshot)])


def _status_icon(status: WorkflowAgentStatus) -> str:
    icons = {"queued": "○", "running": "●", "done": "✓", "error": "✗", "skipped": "-"}
    return icons.get(status, "?")


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for v in values:
        if v not in seen:
            seen.add(v)
            result.append(v)
    return result


def _shorten(value: str, max_len: int) -> str:
    text = " ".join(value.split())
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text
