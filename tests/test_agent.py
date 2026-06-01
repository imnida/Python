import asyncio
import pytest

from dynamic_workflows.agent import EchoAgent, _minimal_for_schema, _build_prompt
from dynamic_workflows.types import AgentOptions


def _run(coro):
    return asyncio.run(coro)


def test_echo_agent_returns_prompt():
    agent = EchoAgent()
    result = _run(agent.run("hello world", AgentOptions()))
    assert "hello world" in result


def test_echo_agent_with_label():
    agent = EchoAgent()
    opts = AgentOptions(label="my-task")
    result = _run(agent.run("do stuff", opts))
    assert isinstance(result, str)


def test_echo_agent_structured_output_object():
    agent = EchoAgent()
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "count": {"type": "integer"},
        },
    }
    result = _run(agent.run("find something", AgentOptions(schema=schema)))
    assert isinstance(result, dict)
    assert "name" in result
    assert "count" in result


def test_echo_agent_structured_output_array():
    agent = EchoAgent()
    schema = {"type": "array"}
    result = _run(agent.run("list items", AgentOptions(schema=schema)))
    assert result == []


def test_minimal_for_schema_object():
    schema = {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "integer"},
            "c": {"type": "boolean"},
            "d": {"type": "array"},
        },
    }
    result = _minimal_for_schema(schema)
    assert result == {"a": "", "b": 0, "c": False, "d": []}


def test_minimal_for_schema_nested():
    schema = {
        "type": "object",
        "properties": {
            "inner": {
                "type": "object",
                "properties": {"x": {"type": "string"}},
            }
        },
    }
    result = _minimal_for_schema(schema)
    assert result == {"inner": {"x": ""}}


def test_build_prompt_basic():
    prompt = _build_prompt("Do the thing", AgentOptions(), None)
    assert "Do the thing" in prompt


def test_build_prompt_with_phase():
    prompt = _build_prompt("Do it", AgentOptions(phase="Step 1"), None)
    assert "Step 1" in prompt
    assert "Do it" in prompt


def test_build_prompt_with_label():
    prompt = _build_prompt("Do it", AgentOptions(label="my-label"), None)
    assert "my-label" in prompt


def test_build_prompt_structured_output_contract():
    prompt = _build_prompt("Find files", AgentOptions(schema={"type": "object"}), None)
    assert "structured_output" in prompt


def test_build_prompt_with_default_instructions():
    prompt = _build_prompt("Do it", AgentOptions(), "System: be brief")
    assert "System: be brief" in prompt
    assert "Do it" in prompt


def test_build_prompt_ordering():
    prompt = _build_prompt(
        "Main task",
        AgentOptions(phase="Phase1", label="lbl", instructions="Per-agent note"),
        "Global instructions",
    )
    idx_global = prompt.index("Global instructions")
    idx_per_agent = prompt.index("Per-agent note")
    idx_phase = prompt.index("Phase1")
    idx_label = prompt.index("lbl")
    idx_task = prompt.index("Main task")
    assert idx_global < idx_per_agent < idx_phase < idx_label < idx_task
