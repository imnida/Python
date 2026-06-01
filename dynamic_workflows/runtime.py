from __future__ import annotations

import asyncio
import time
from typing import Any, Callable, Coroutine, Optional

from .agent import AnthropicAgent, BaseWorkflowAgent, EchoAgent
from .display import WorkflowDisplay, create_text_display, recompute_snapshot
from .types import (
    AgentOptions,
    WorkflowAgentSnapshot,
    WorkflowMeta,
    WorkflowRunResult,
    WorkflowSnapshot,
)

DEFAULT_CONCURRENCY = 8
MAX_CONCURRENCY = 16


class WorkflowRunOptions:
    def __init__(
        self,
        *,
        agent: Optional[BaseWorkflowAgent] = None,
        concurrency: int = DEFAULT_CONCURRENCY,
        token_budget: Optional[int] = None,
        args: Optional[Any] = None,
        cwd: Optional[str] = None,
        on_log: Optional[Callable[[str], None]] = None,
        on_phase: Optional[Callable[[str], None]] = None,
        on_agent_start: Optional[Callable[[dict], None]] = None,
        on_agent_end: Optional[Callable[[dict], None]] = None,
        display: Optional[WorkflowDisplay] = None,
    ) -> None:
        self.agent = agent or AnthropicAgent()
        self.concurrency = max(1, min(concurrency, MAX_CONCURRENCY))
        self.token_budget = token_budget
        self.args = args
        self.cwd = cwd
        self.on_log = on_log
        self.on_phase = on_phase
        self.on_agent_start = on_agent_start
        self.on_agent_end = on_agent_end
        self.display = display


class _Limiter:
    def __init__(self, limit: int) -> None:
        self._sem = asyncio.Semaphore(limit)

    async def run(self, coro: Coroutine) -> Any:
        async with self._sem:
            return await coro


class _RuntimeState:
    def __init__(self) -> None:
        self.current_phase: Optional[str] = None
        self.logs: list[str] = []
        self.phases: list[str] = []
        self.agents: list[WorkflowAgentSnapshot] = []
        self._agent_counter = 0
        self.spent = 0

    def next_agent_id(self) -> int:
        self._agent_counter += 1
        return self._agent_counter


async def run_workflow(
    fn: Callable[[], Coroutine],
    meta: WorkflowMeta,
    options: Optional[WorkflowRunOptions] = None,
) -> WorkflowRunResult:
    """Run a workflow coroutine function with the given meta and options."""
    if options is None:
        options = WorkflowRunOptions()

    started = time.monotonic()
    state = _RuntimeState()
    limiter = _Limiter(options.concurrency)
    snapshot = WorkflowSnapshot(
        name=meta.name,
        description=meta.description,
        phases=[],
        logs=[],
        agents=[],
        agent_count=0,
        running_count=0,
        done_count=0,
        error_count=0,
    )

    def _emit_snapshot() -> None:
        if options.display:
            updated = recompute_snapshot(snapshot)
            snapshot.__dict__.update(updated.__dict__)
            options.display.update(snapshot)

    def _log(message: str) -> None:
        text = str(message)
        state.logs.append(text)
        snapshot.logs = state.logs[:]
        options.on_log and options.on_log(text)
        _emit_snapshot()

    def _phase(title: str) -> None:
        if not isinstance(title, str):
            raise TypeError(f"phase title must be a string, got {type(title).__name__}")
        state.current_phase = title
        if title not in state.phases:
            state.phases.append(title)
        snapshot.current_phase = title
        snapshot.phases = state.phases[:]
        options.on_phase and options.on_phase(title)
        _emit_snapshot()

    async def _agent(prompt: str, *, label: Optional[str] = None, schema: Optional[dict] = None,
                     model: Optional[str] = None, phase: Optional[str] = None,
                     instructions: Optional[str] = None, **_: Any) -> Any:
        if not isinstance(prompt, str):
            raise TypeError(f"agent prompt must be a string, got {type(prompt).__name__}")
        if options.token_budget is not None and state.spent >= options.token_budget:
            raise RuntimeError("workflow token budget exhausted")

        assigned_phase = phase or state.current_phase
        agent_id = state.next_agent_id()
        effective_label = (label or "").strip() or _default_label(assigned_phase, agent_id)
        snap = WorkflowAgentSnapshot(
            id=agent_id,
            label=effective_label,
            prompt=prompt,
            status="queued",
            phase=assigned_phase,
        )
        state.agents.append(snap)
        snapshot.agents = state.agents[:]
        _emit_snapshot()

        async def _run() -> Any:
            snap.status = "running"
            _emit_snapshot()
            options.on_agent_start and options.on_agent_start(
                {"label": effective_label, "phase": assigned_phase, "prompt": prompt}
            )
            try:
                result = await options.agent.run(
                    prompt,
                    AgentOptions(
                        label=effective_label,
                        phase=assigned_phase,
                        schema=schema,
                        model=model,
                        instructions=instructions,
                    ),
                )
                snap.status = "done"
                snap.result_preview = _preview(result)
                state.spent += _estimate_tokens(result)
                options.on_agent_end and options.on_agent_end(
                    {"label": effective_label, "phase": assigned_phase, "result": result}
                )
                _emit_snapshot()
                return result
            except Exception as exc:
                snap.status = "error"
                snap.error = str(exc)
                _log(f"agent {effective_label} failed: {exc}")
                options.on_agent_end and options.on_agent_end(
                    {"label": effective_label, "phase": assigned_phase, "result": None}
                )
                _emit_snapshot()
                return None

        return await limiter.run(_run())

    async def _parallel(thunks: list[Callable]) -> list[Any]:
        if not isinstance(thunks, list):
            raise TypeError("parallel() expects a list of callables")
        for i, t in enumerate(thunks):
            if not callable(t):
                raise TypeError(
                    f"parallel() expects callables (lambdas), not values. "
                    f"Wrap each call: lambda: agent(...)  (item {i} is {type(t).__name__})"
                )

        async def _safe(thunk: Callable, index: int) -> Any:
            try:
                return await thunk()
            except Exception as exc:
                _log(f"parallel[{index}] failed: {exc}")
                return None

        return await asyncio.gather(*[_safe(t, i) for i, t in enumerate(thunks)])

    async def _pipeline(items: list, *stages: Callable) -> list[Any]:
        if not isinstance(items, list):
            raise TypeError("pipeline() expects a list as the first argument")
        for stage in stages:
            if not callable(stage):
                raise TypeError("pipeline() stages must be callables")

        async def _run_item(item: Any, index: int) -> Any:
            value = item
            for stage in stages:
                try:
                    value = await stage(value, item, index)
                except Exception as exc:
                    _log(f"pipeline[{index}] failed: {exc}")
                    return None
            return value

        return await asyncio.gather(*[_run_item(item, i) for i, item in enumerate(items)])

    workflow_globals = {
        "agent": _agent,
        "parallel": _parallel,
        "pipeline": _pipeline,
        "phase": _phase,
        "log": _log,
        "args": options.args,
        "cwd": options.cwd,
        "budget": _Budget(options.token_budget, state),
    }

    # Patch the function's globals temporarily so `agent`, `phase`, etc. resolve
    fn_globals = getattr(fn, "__globals__", {})
    _saved = {k: fn_globals.get(k) for k in workflow_globals}
    fn_globals.update(workflow_globals)
    try:
        result = await fn()
    finally:
        for k, v in _saved.items():
            if v is None:
                fn_globals.pop(k, None)
            else:
                fn_globals[k] = v

    duration_ms = (time.monotonic() - started) * 1000
    if options.display:
        snapshot.result = result
        snapshot.duration_ms = duration_ms
        final = recompute_snapshot(snapshot)
        options.display.complete(final)

    return WorkflowRunResult(
        meta=meta,
        result=result,
        logs=state.logs[:],
        phases=state.phases[:],
        agent_count=state._agent_counter,
        duration_ms=duration_ms,
    )


class _Budget:
    def __init__(self, total: Optional[int], state: _RuntimeState) -> None:
        self.total = total
        self._state = state

    def spent(self) -> int:
        return self._state.spent

    def remaining(self) -> float:
        if self.total is None:
            return float("inf")
        return max(0, self.total - self._state.spent)


def _default_label(phase: Optional[str], index: int) -> str:
    return f"{phase} agent {index}" if phase else f"agent {index}"


def _preview(value: Any, max_len: int = 80) -> str:
    text = value if isinstance(value, str) else str(value)
    if len(text) > max_len:
        return text[: max_len - 1] + "…"
    return text


def _estimate_tokens(value: Any) -> int:
    import json as _json
    try:
        return max(1, len(_json.dumps(value, default=str)) // 4)
    except Exception:
        return 1
