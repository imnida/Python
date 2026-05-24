"""
Fault injection simulation for distributed system tests.

Provides nemesis patterns (network partition, node crash, clock skew, etc.)
that can be applied to a simulated cluster. Each nemesis captures landing
evidence so the oracle can confirm the fault was active during the test window.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class FaultType(Enum):
    NETWORK_PARTITION = "network-partition"
    NODE_CRASH = "node-crash"
    CLOCK_SKEW = "clock-skew"
    DISK_SLOW = "disk-slow"
    MESSAGE_DELAY = "message-delay"
    MESSAGE_DROP = "message-drop"
    LEADER_KILL = "leader-kill"
    ASYMMETRIC_PARTITION = "asymmetric-partition"


@dataclass
class LandingEvidence:
    """Observable signal confirming a fault actually took effect."""

    fault_type: FaultType
    affected_nodes: list[str]
    signal: str
    timestamp: float = field(default_factory=time.time)
    metric_value: Optional[float] = None

    @property
    def proven(self) -> bool:
        return bool(self.signal and self.affected_nodes)


@dataclass
class Nemesis:
    """
    A scheduled fault injection plan for a scenario.

    The nemesis fires at start_offset seconds into the workload,
    holds for duration seconds, then heals.
    """

    fault_type: FaultType
    target_nodes: list[str]
    start_offset: float = 10.0
    duration: float = 30.0
    description: str = ""

    def describe(self) -> str:
        return (
            f"{self.fault_type.value} on {self.target_nodes} "
            f"for {self.duration}s starting at t+{self.start_offset}s"
        )


class FaultInjector:
    """
    Simulates fault injection against a cluster, producing landing evidence.

    In a real harness this wraps iptables, tc/netem, kill(1), or Toxiproxy.
    This implementation is a pure-Python simulation suitable for unit tests
    and demonstration.
    """

    def __init__(self, random_seed: int = 42) -> None:
        self._rng = random.Random(random_seed)
        self._active_faults: list[tuple[Nemesis, LandingEvidence]] = []

    def inject(self, nemesis: Nemesis) -> LandingEvidence:
        """Apply a nemesis and return landing evidence."""
        evidence = self._simulate_injection(nemesis)
        self._active_faults.append((nemesis, evidence))
        return evidence

    def heal(self, nemesis: Nemesis) -> None:
        self._active_faults = [(n, e) for n, e in self._active_faults if n is not nemesis]

    def active_faults(self) -> list[Nemesis]:
        return [n for n, _ in self._active_faults]

    def all_evidence(self) -> list[LandingEvidence]:
        return [e for _, e in self._active_faults]

    def _simulate_injection(self, nemesis: Nemesis) -> LandingEvidence:
        if nemesis.fault_type == FaultType.NETWORK_PARTITION:
            signal = f"iptables DROP rule installed; packet counter={self._rng.randint(50, 500)}"
            metric = self._rng.uniform(0.9, 1.0)
        elif nemesis.fault_type == FaultType.NODE_CRASH:
            signal = f"SIGKILL sent; process exited with status 137"
            metric = None
        elif nemesis.fault_type == FaultType.CLOCK_SKEW:
            skew_ms = self._rng.randint(100, 5000)
            signal = f"libfaketime offset applied: +{skew_ms}ms"
            metric = float(skew_ms)
        elif nemesis.fault_type == FaultType.DISK_SLOW:
            delay_ms = self._rng.randint(50, 2000)
            signal = f"dm-flakey delay={delay_ms}ms on /dev/sdb"
            metric = float(delay_ms)
        elif nemesis.fault_type in {FaultType.MESSAGE_DELAY, FaultType.MESSAGE_DROP}:
            rate = self._rng.uniform(0.1, 0.5)
            signal = f"tc netem {nemesis.fault_type.value} rate={rate:.1%}"
            metric = rate
        elif nemesis.fault_type == FaultType.LEADER_KILL:
            signal = f"Leader node killed; new election observed in logs"
            metric = None
        elif nemesis.fault_type == FaultType.ASYMMETRIC_PARTITION:
            signal = f"iptables INPUT DROP on {nemesis.target_nodes}; OUTPUT allowed"
            metric = None
        else:
            signal = f"Unknown fault type: {nemesis.fault_type}"
            metric = None

        return LandingEvidence(
            fault_type=nemesis.fault_type,
            affected_nodes=nemesis.target_nodes,
            signal=signal,
            metric_value=metric,
        )
