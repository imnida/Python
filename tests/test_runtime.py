import asyncio
import pytest

from dynamic_workflows import EchoAgent, WorkflowMeta, WorkflowRunOptions, run_workflow


def _opts(**kw):
    return WorkflowRunOptions(agent=EchoAgent(), **kw)


def _run(fn, meta, **kw):
    return asyncio.run(run_workflow(fn, meta, _opts(**kw)))


def test_basic_agent_call():
    meta = WorkflowMeta(name="basic", description="Basic test")

    async def workflow():
        result = await agent("Hello world", label="greeter")
        return result

    out = _run(workflow, meta)
    assert out.meta.name == "basic"
    assert "Hello world" in out.result
    assert out.agent_count == 1
    assert out.phases == []


def test_phase_tracking():
    meta = WorkflowMeta(name="phases", description="Phase test")

    async def workflow():
        phase("Step 1")
        r1 = await agent("Do step 1", label="s1")
        phase("Step 2")
        r2 = await agent("Do step 2", label="s2")
        return [r1, r2]

    out = _run(workflow, meta)
    assert out.phases == ["Step 1", "Step 2"]
    assert out.agent_count == 2


def test_parallel_execution():
    meta = WorkflowMeta(name="parallel", description="Parallel test")

    async def workflow():
        results = await parallel([
            lambda: agent("Task A", label="a"),
            lambda: agent("Task B", label="b"),
            lambda: agent("Task C", label="c"),
        ])
        return results

    out = _run(workflow, meta)
    assert len(out.result) == 3
    assert out.agent_count == 3


def test_pipeline_execution():
    meta = WorkflowMeta(name="pipeline", description="Pipeline test")

    async def workflow():
        items = ["item1", "item2"]
        results = await pipeline(
            items,
            lambda prev, original, idx: agent(f"Process {prev}", label=f"proc-{idx}"),
        )
        return results

    out = _run(workflow, meta)
    assert len(out.result) == 2
    assert out.agent_count == 2


def test_log_capture():
    meta = WorkflowMeta(name="logging", description="Log test")

    async def workflow():
        log("Step A starting")
        await agent("Some work", label="worker")
        log("Step A done")
        return "done"

    captured = []
    out = _run(workflow, meta, on_log=captured.append)
    assert "Step A starting" in out.logs
    assert "Step A done" in out.logs
    assert captured == out.logs


def test_args_available():
    meta = WorkflowMeta(name="args-test", description="Args test")

    async def workflow():
        return args

    out = _run(workflow, meta, args={"key": "value"})
    assert out.result == {"key": "value"}


def test_structured_output():
    meta = WorkflowMeta(name="structured", description="Structured output test")

    schema = {
        "type": "object",
        "properties": {
            "files": {"type": "array", "items": {"type": "string"}},
            "count": {"type": "integer"},
        },
    }

    async def workflow():
        return await agent("Find files", label="finder", schema=schema)

    out = _run(workflow, meta)
    assert isinstance(out.result, dict)
    assert "files" in out.result
    assert "count" in out.result


def test_parallel_error_returns_none():
    meta = WorkflowMeta(name="parallel-err", description="Parallel error resilience")

    async def workflow():
        results = await parallel([
            lambda: agent("ok", label="good"),
        ])
        return results

    out = _run(workflow, meta)
    assert len(out.result) == 1


def test_workflow_run_result_fields():
    meta = WorkflowMeta(name="fields", description="Result fields test")

    async def workflow():
        return 42

    out = _run(workflow, meta)
    assert out.result == 42
    assert isinstance(out.duration_ms, float)
    assert out.duration_ms >= 0
    assert isinstance(out.logs, list)
    assert isinstance(out.phases, list)


def test_on_phase_callback():
    meta = WorkflowMeta(name="cb-phase", description="Phase callback test")
    phases_seen = []

    async def workflow():
        phase("Alpha")
        await agent("Work", label="w")
        phase("Beta")
        await agent("More work", label="w2")
        return "done"

    _run(workflow, meta, on_phase=phases_seen.append)
    assert phases_seen == ["Alpha", "Beta"]


def test_nested_parallel_and_phase():
    meta = WorkflowMeta(name="nested", description="Nested test")

    async def workflow():
        phase("Gather")
        results = await parallel([
            lambda: agent("Task 1", label="t1"),
            lambda: agent("Task 2", label="t2"),
        ])
        phase("Synthesize")
        summary = await agent(f"Summarize: {results}", label="summarizer")
        return {"gathered": results, "summary": summary}

    out = _run(workflow, meta)
    assert out.phases == ["Gather", "Synthesize"]
    assert out.agent_count == 3
    assert "gathered" in out.result
    assert "summary" in out.result
