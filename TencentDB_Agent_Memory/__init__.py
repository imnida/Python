"""TencentDB Agent Memory — Python SDK.

Four-layer agent memory system:
  L0  Raw conversation records
  L1  Atomic extracted facts
  L2  Scene / scenario blocks
  L3  Persona synthesis

Requires the memory-tencentdb Node.js Gateway sidecar.
Quick start:

    from TencentDB_Agent_Memory import MemoryClient
    mem = MemoryClient()
    mem.capture("user said X", "assistant replied Y", session_key="my-session")
    results = mem.search_memories("user preferences")
"""

from .client import MemoryTencentdbSdkClient
from .supervisor import GatewaySupervisor
from .provider import MemoryTencentdbProvider, MemoryClient

__all__ = [
    "MemoryTencentdbSdkClient",
    "GatewaySupervisor",
    "MemoryTencentdbProvider",
    "MemoryClient",
]
