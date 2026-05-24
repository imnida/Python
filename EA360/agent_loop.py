"""
EA360 agent loop backed by a local Ollama model.

The loop is intentionally minimal and immutable (Template Method pattern):
the LLM decides, the harness executes.  Variation comes from swapping
TOOLS / HANDLERS, not from changing this file.

Usage:
    python -m EA360.agent_loop
    # or
    from EA360.agent_loop import run
    run("Model the OrderProcessing system with TOGAF compliance.")
"""

from __future__ import annotations

import json
import sys
from typing import Any

import ollama

from .harness import HANDLERS, TOOLS

MODEL = "llama3.2"  # swap for any Ollama-hosted model

SYSTEM_PROMPT = """You are EA360, an Enterprise Architecture assistant.
You help architects design, validate, and evolve architectures that comply
with TOGAF 10 and ArchiMate 3.2.

Rules:
- Always validate_togaf before exporting.
- When creating a DataObject, confirm sensitivity and owner with the user first.
- Prefer specific ArchiMate relationship types over 'associated_with'.
- Explain each tool call briefly in plain language before invoking it.
"""


def _call_tool(name: str, inputs: dict[str, Any]) -> str:
    handler = HANDLERS.get(name)
    if handler is None:
        return json.dumps({"error": f"Unknown tool: {name}"})
    result = handler(**inputs)
    return json.dumps(result, ensure_ascii=False)


def run(user_message: str, verbose: bool = True) -> str:
    """
    Run the EA360 agent loop for a single user request.

    The loop continues until the model stops requesting tools.

    Args:
        user_message: Natural language architecture request.
        verbose: Print each assistant turn and tool call to stdout.

    Returns:
        str: Final plain-text response from the model.
    """
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    while True:
        response = ollama.chat(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
        )
        msg = response["message"]
        messages.append(msg)

        if not msg.get("tool_calls"):
            final = msg.get("content", "")
            if verbose:
                print(f"\nEA360: {final}")
            return final

        for call in msg["tool_calls"]:
            name = call["function"]["name"]
            inputs = call["function"]["arguments"]
            if verbose:
                print(f"  → {name}({json.dumps(inputs, ensure_ascii=False)})")
            result = _call_tool(name, inputs)
            if verbose:
                print(f"    ← {result}")
            messages.append({
                "role": "tool",
                "content": result,
                "name": name,
            })


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else (
        "Create a CustomerDataHub DataObject owned by the DMO team "
        "with confidential sensitivity, then validate the model."
    )
    run(prompt)
