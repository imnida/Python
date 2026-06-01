from __future__ import annotations

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any, Optional

from .types import AgentOptions


class BaseWorkflowAgent(ABC):
    """Abstract base for workflow agent backends."""

    @abstractmethod
    async def run(self, prompt: str, options: AgentOptions) -> Any:
        ...


class EchoAgent(BaseWorkflowAgent):
    """Test agent that echoes the prompt back."""

    async def run(self, prompt: str, options: AgentOptions) -> Any:
        await asyncio.sleep(0)
        if options.schema:
            return _minimal_for_schema(options.schema)
        return f"[echo] {prompt}"


class AnthropicAgent(BaseWorkflowAgent):
    """Agent backed by the Anthropic Claude API."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-6",
        api_key: Optional[str] = None,
        cwd: Optional[str] = None,
        default_instructions: Optional[str] = None,
    ) -> None:
        self._model = model
        self._api_key = api_key
        self._cwd = cwd
        self._default_instructions = default_instructions

    async def run(self, prompt: str, options: AgentOptions) -> Any:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError(
                "anthropic package is required for AnthropicAgent: pip install anthropic"
            ) from exc

        client = anthropic.AsyncAnthropic(api_key=self._api_key) if self._api_key else anthropic.AsyncAnthropic()
        model = options.model or self._model
        full_prompt = _build_prompt(prompt, options, self._default_instructions)

        if options.schema:
            return await self._run_structured(client, model, full_prompt, options.schema)

        message = await client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[{"role": "user", "content": full_prompt}],
        )
        return message.content[0].text if message.content else ""

    async def _run_structured(self, client: Any, model: str, prompt: str, schema: dict) -> Any:
        tool = {
            "name": "structured_output",
            "description": "Return your final structured answer.",
            "input_schema": schema,
        }
        message = await client.messages.create(
            model=model,
            max_tokens=4096,
            tools=[tool],
            tool_choice={"type": "any"},
            messages=[{"role": "user", "content": prompt}],
        )
        for block in message.content:
            if getattr(block, "type", None) == "tool_use" and block.name == "structured_output":
                return block.input
        raise RuntimeError("Subagent finished without calling structured_output")


def _build_prompt(
    prompt: str,
    options: AgentOptions,
    default_instructions: Optional[str],
) -> str:
    parts: list[str] = []
    if default_instructions:
        parts.append(default_instructions)
    if options.instructions:
        parts.append(options.instructions)
    if options.phase:
        parts.append(f"Workflow phase: {options.phase}")
    if options.label:
        parts.append(f"Task label: {options.label}")
    parts.append(prompt)
    if options.schema:
        parts.append(
            "Final output contract:\n"
            "- Your final action MUST be a structured_output tool call.\n"
            "- Do not emit a prose final answer instead of structured_output."
        )
    return "\n\n".join(parts)


def _minimal_for_schema(schema: dict) -> Any:
    """Produce a minimal valid value for a JSON Schema (used by EchoAgent)."""
    t = schema.get("type")
    if t == "object":
        result = {}
        for key, prop in schema.get("properties", {}).items():
            result[key] = _minimal_for_schema(prop)
        return result
    if t == "array":
        return []
    if t == "string":
        return ""
    if t == "number" or t == "integer":
        return 0
    if t == "boolean":
        return False
    return None
