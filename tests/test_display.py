from dynamic_workflows.display import (
    render_workflow_lines,
    render_workflow_text,
    recompute_snapshot,
)
from dynamic_workflows.types import WorkflowAgentSnapshot, WorkflowSnapshot


def _snapshot(**kw) -> WorkflowSnapshot:
    defaults = dict(
        name="test",
        description="Test workflow",
        phases=[],
        current_phase=None,
        logs=[],
        agents=[],
        agent_count=0,
        running_count=0,
        done_count=0,
        error_count=0,
    )
    defaults.update(kw)
    return WorkflowSnapshot(**defaults)


def _agent(id, label, status, phase=None) -> WorkflowAgentSnapshot:
    return WorkflowAgentSnapshot(id=id, label=label, prompt="...", status=status, phase=phase)


def test_empty_snapshot():
    s = _snapshot()
    lines = render_workflow_lines(s)
    assert lines[0] == "◆ Workflow: test (0/0 done)"


def test_running_state_in_header():
    a = _agent(1, "worker", "running", phase="Scan")
    s = _snapshot(
        phases=["Scan"],
        current_phase="Scan",
        agents=[a],
        agent_count=1,
        running_count=1,
        done_count=0,
        error_count=0,
    )
    lines = render_workflow_lines(s)
    assert "1 running" in lines[0]


def test_error_count_in_header():
    a = _agent(1, "worker", "error", phase="Scan")
    s = _snapshot(
        phases=["Scan"],
        agents=[a],
        agent_count=1,
        running_count=0,
        done_count=0,
        error_count=1,
    )
    lines = render_workflow_lines(s)
    assert "1 errors" in lines[0]


def test_phase_groups_shown():
    a1 = _agent(1, "scanner", "done", phase="Scan")
    a2 = _agent(2, "analyzer", "done", phase="Analyze")
    s = _snapshot(
        phases=["Scan", "Analyze"],
        agents=[a1, a2],
        agent_count=2,
        running_count=0,
        done_count=2,
        error_count=0,
    )
    lines = render_workflow_lines(s)
    text = "\n".join(lines)
    assert "Scan" in text
    assert "Analyze" in text


def test_unphased_agents_shown():
    a = _agent(1, "mystery", "done")
    s = _snapshot(agents=[a], agent_count=1, done_count=1)
    lines = render_workflow_lines(s)
    text = "\n".join(lines)
    assert "Unphased" in text
    assert "mystery" in text


def test_log_lines_shown():
    s = _snapshot(logs=["first log", "second log"])
    lines = render_workflow_lines(s, max_logs=2)
    text = "\n".join(lines)
    assert "first log" in text
    assert "second log" in text


def test_log_truncation():
    s = _snapshot(logs=["a", "b", "c", "d"])
    lines = render_workflow_lines(s, max_logs=2)
    text = "\n".join(lines)
    assert "c" in text
    assert "d" in text
    assert "a" not in text


def test_recompute_snapshot_counts():
    agents = [
        _agent(1, "a", "done"),
        _agent(2, "b", "running"),
        _agent(3, "c", "error"),
        _agent(4, "d", "queued"),
    ]
    s = _snapshot(agents=agents)
    updated = recompute_snapshot(s)
    assert updated.done_count == 1
    assert updated.running_count == 1
    assert updated.error_count == 1
    assert updated.agent_count == 4


def test_render_workflow_text_header():
    s = _snapshot()
    text = render_workflow_text(s, completed=False)
    assert text.startswith("Workflow running")

    text_done = render_workflow_text(s, completed=True)
    assert text_done.startswith("Workflow completed")


def test_phase_marker_complete():
    a = _agent(1, "worker", "done", phase="Phase1")
    s = _snapshot(phases=["Phase1"], agents=[a], agent_count=1, done_count=1)
    lines = render_workflow_lines(s)
    phase_line = next(l for l in lines if "Phase1" in l)
    assert "✓" in phase_line


def test_phase_marker_running():
    a = _agent(1, "worker", "running", phase="Phase1")
    s = _snapshot(
        phases=["Phase1"],
        current_phase="Phase1",
        agents=[a],
        agent_count=1,
        running_count=1,
    )
    lines = render_workflow_lines(s)
    phase_line = next(l for l in lines if "Phase1" in l)
    assert "▶" in phase_line


def test_status_icons():
    statuses = [("done", "✓"), ("running", "●"), ("queued", "○"), ("error", "✗"), ("skipped", "-")]
    for status, icon in statuses:
        a = _agent(1, "w", status)
        s = _snapshot(agents=[a], agent_count=1)
        lines = render_workflow_lines(s)
        text = "\n".join(lines)
        assert icon in text, f"Expected {icon!r} for status {status!r}"


def test_agent_label_truncated():
    long_label = "a" * 100
    a = _agent(1, long_label, "done")
    s = _snapshot(agents=[a], agent_count=1, done_count=1)
    lines = render_workflow_lines(s)
    text = "\n".join(lines)
    assert "…" in text
