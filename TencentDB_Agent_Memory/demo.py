"""TencentDB Agent Memory — interactive demo.

Demonstrates the four-layer memory system:
  L0  Raw conversation capture
  L1  Structured memory search
  L2  Scene-level recall
  L3  Persona retrieval

Prerequisites:
  1. Install the memory-tencentdb Node.js plugin (OpenClaw or standalone).
  2. Start the Gateway:
       openclaw gateway start
     or set MEMORY_TENCENTDB_GATEWAY_CMD and let the provider auto-start it.
  3. Run this script:
       python demo.py

The demo will also work with just the HTTP client if the Gateway is already
running (no auto-start needed).
"""

from __future__ import annotations

import json
import logging
import sys
import time

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)

from TencentDB_Agent_Memory import MemoryClient
from TencentDB_Agent_Memory.client import MemoryTencentdbSdkClient


def check_gateway(gateway_url: str = "http://127.0.0.1:8420") -> bool:
    """Return True if the Gateway is reachable."""
    client = MemoryTencentdbSdkClient(base_url=gateway_url, timeout=3)
    try:
        result = client.health(timeout=3)
        status = result.get("status", "unknown")
        print(f"Gateway health: {status}")
        if "version" in result:
            print(f"  version : {result['version']}")
        if "uptime" in result:
            print(f"  uptime  : {result['uptime']}s")
        return status in ("ok", "degraded")
    except Exception as e:
        print(f"Gateway not reachable: {e}")
        return False


def demo_capture_and_recall(mem: MemoryClient) -> None:
    """Capture a few conversation turns, then recall them."""
    print("\n--- Capturing conversation turns ---")
    turns = [
        ("What is the capital of France?", "The capital of France is Paris."),
        ("I prefer dark mode in my editor.", "Noted — I'll use dark mode in future code examples."),
        ("My tech stack is Python + FastAPI + PostgreSQL.", "Got it. I'll tailor examples accordingly."),
        ("Can you remind me about my editor preferences?", "You prefer dark mode in your editor."),
    ]

    for user, assistant in turns:
        print(f"  USER      : {user[:60]}")
        print(f"  ASSISTANT : {assistant[:60]}")
        mem.capture(user, assistant)
        time.sleep(0.1)  # let the background thread dispatch

    print("\n--- Recalling memories: 'editor preferences' ---")
    context = mem.recall("editor preferences")
    if context:
        print(context)
    else:
        print("  (no memories recalled — try again after memory extraction runs)")


def demo_search_memories(mem: MemoryClient) -> None:
    """Search structured L1 memories."""
    print("\n--- Searching structured memories: 'tech stack' ---")
    results = mem.search("tech stack", limit=5)
    if results:
        for i, r in enumerate(results, 1):
            content = r.get("content") or r.get("text") or json.dumps(r)[:80]
            print(f"  {i}. {content[:100]}")
    else:
        print("  (no results — memory extraction may still be running)")


def demo_search_conversations(mem: MemoryClient) -> None:
    """Search raw L0 conversation history."""
    print("\n--- Searching conversations: 'dark mode' ---")
    msgs = mem.search_conversations("dark mode", limit=3)
    if msgs:
        for i, m in enumerate(msgs, 1):
            role = m.get("role", "?")
            content = m.get("content", json.dumps(m)[:80])
            print(f"  {i}. [{role}] {content[:100]}")
    else:
        print("  (no conversation records found)")


def demo_seed(gateway_url: str = "http://127.0.0.1:8420") -> None:
    """Seed a batch of historical conversations via the /seed endpoint."""
    print("\n--- Seeding historical conversations ---")
    client = MemoryTencentdbSdkClient(base_url=gateway_url, timeout=60)

    historical = {
        "sessions": [
            {
                "session_key": "history-demo-001",
                "rounds": [
                    {
                        "user": "I always use type hints in Python.",
                        "assistant": "Understood. I'll include type hints in all code I write for you.",
                    },
                    {
                        "user": "I prefer pytest over unittest.",
                        "assistant": "Got it — I'll use pytest for all tests.",
                    },
                ],
            }
        ]
    }

    try:
        result = client.seed(data=historical, session_key="history-demo-001", timeout=120)
        print(f"  Seed result: {result}")
    except Exception as e:
        print(f"  Seed failed (Gateway may not be running): {e}")


def main() -> None:
    gateway_url = "http://127.0.0.1:8420"

    print("=" * 60)
    print("TencentDB Agent Memory — Python SDK Demo")
    print("=" * 60)

    # 1. Check Gateway connectivity
    print("\n[1] Gateway health check")
    available = check_gateway(gateway_url)
    if not available:
        print(
            "\nGateway is not running. Start it with:\n"
            "  openclaw gateway start\n"
            "or set MEMORY_TENCENTDB_GATEWAY_CMD and run again.\n"
            "Running in offline-demo mode (API calls will be no-ops)."
        )

    # 2. MemoryClient demo
    print("\n[2] MemoryClient (high-level API)")
    with MemoryClient(
        session_id="python-sdk-demo",
        user_id="demo-user",
        gateway_url=gateway_url,
    ) as mem:
        print(f"  connected: {mem.connected}")
        demo_capture_and_recall(mem)
        demo_search_memories(mem)
        demo_search_conversations(mem)

    # 3. Seed API demo
    print("\n[3] Seed API (batch historical conversations)")
    demo_seed(gateway_url)

    print("\n[4] Raw HTTP client usage")
    client = MemoryTencentdbSdkClient(base_url=gateway_url)
    try:
        result = client.search_memories(query="Python preferences", limit=3)
        print(f"  search_memories result: {json.dumps(result, indent=2)[:200]}")
    except Exception as e:
        print(f"  search_memories: {e} (Gateway not running)")

    print("\nDemo complete.")


if __name__ == "__main__":
    main()
