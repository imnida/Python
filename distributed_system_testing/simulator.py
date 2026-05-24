"""
Simple distributed system simulator for testing oracle patterns.

Models a replicated key-value store with configurable consistency levels.
Not production-grade — designed to produce operation histories that can
be checked by linearizability and monotonic-read oracles.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class NodeState(Enum):
    LEADER = "leader"
    FOLLOWER = "follower"
    CRASHED = "crashed"
    PARTITIONED = "partitioned"


@dataclass
class Operation:
    """One recorded operation in the history (11 canonical fields)."""

    op_id: str
    process_id: str
    invoke_ts: float
    complete_ts: Optional[float]
    op_type: str
    key: str
    input_value: Any
    output_value: Any
    error: Optional[str]
    timeout_marker: bool
    node_seen: Optional[str]
    fault_epoch: int = 0

    @property
    def duration_ms(self) -> Optional[float]:
        if self.complete_ts is None:
            return None
        return (self.complete_ts - self.invoke_ts) * 1000


class OperationHistory:
    """Ordered sequence of operations for oracle consumption."""

    def __init__(self) -> None:
        self._ops: list[Operation] = []

    def record(self, op: Operation) -> None:
        self._ops.append(op)

    def all_ops(self) -> list[Operation]:
        return list(self._ops)

    def ops_by_key(self, key: str) -> list[Operation]:
        return [o for o in self._ops if o.key == key]

    def completed_ops(self) -> list[Operation]:
        return [o for o in self._ops if not o.timeout_marker and o.error is None]

    def has_required_fields(self) -> bool:
        """Checks that every operation carries the 11 canonical history fields."""
        for op in self._ops:
            if op.op_id is None or op.process_id is None:
                return False
            if op.invoke_ts is None:
                return False
        return True

    def __len__(self) -> int:
        return len(self._ops)


@dataclass
class DistributedNode:
    node_id: str
    state: NodeState = NodeState.FOLLOWER
    store: dict[str, Any] = field(default_factory=dict)
    log: list[tuple[str, Any]] = field(default_factory=list)
    replication_lag: float = 0.0

    def is_available(self) -> bool:
        return self.state not in {NodeState.CRASHED, NodeState.PARTITIONED}

    def write(self, key: str, value: Any) -> bool:
        if not self.is_available():
            return False
        self.log.append((key, value))
        self.store[key] = value
        return True

    def read(self, key: str) -> tuple[bool, Any]:
        if not self.is_available():
            return False, None
        return True, self.store.get(key)

    def apply_replication(self, leader_log: list[tuple[str, Any]]) -> None:
        lag_entries = int(self.replication_lag * len(leader_log))
        synced_log = leader_log[: max(0, len(leader_log) - lag_entries)]
        for k, v in synced_log:
            self.store[k] = v


class Cluster:
    """
    Simulated replicated cluster with configurable failure modes.

    Supports leader election, network partitions, and crash/restart.
    Not a real consensus implementation — designed for test harness use.
    """

    def __init__(self, node_ids: list[str], random_seed: int = 42) -> None:
        self._rng = random.Random(random_seed)
        self.nodes: dict[str, DistributedNode] = {
            nid: DistributedNode(node_id=nid) for nid in node_ids
        }
        self._leader_id: Optional[str] = node_ids[0] if node_ids else None
        if self._leader_id:
            self.nodes[self._leader_id].state = NodeState.LEADER
        else:
            for node in self.nodes.values():
                node.state = NodeState.FOLLOWER
        self._fault_epoch = 0
        self._op_counter = 0

    @property
    def leader(self) -> Optional[DistributedNode]:
        if self._leader_id and self._leader_id in self.nodes:
            n = self.nodes[self._leader_id]
            if n.state == NodeState.LEADER:
                return n
        return None

    def crash_node(self, node_id: str) -> None:
        self.nodes[node_id].state = NodeState.CRASHED
        self._fault_epoch += 1
        if node_id == self._leader_id:
            self._elect_new_leader()

    def restart_node(self, node_id: str) -> None:
        node = self.nodes[node_id]
        node.state = NodeState.FOLLOWER
        if self.leader:
            node.apply_replication(self.leader.log)

    def partition_node(self, node_id: str) -> None:
        self.nodes[node_id].state = NodeState.PARTITIONED
        self._fault_epoch += 1
        if node_id == self._leader_id:
            self._elect_new_leader()

    def heal_node(self, node_id: str) -> None:
        node = self.nodes[node_id]
        node.state = NodeState.FOLLOWER
        if self.leader:
            node.apply_replication(self.leader.log)

    def write(self, key: str, value: Any, process_id: str = "client-0") -> Operation:
        self._op_counter += 1
        op_id = f"op-{self._op_counter}"
        invoke_ts = time.time()

        leader = self.leader
        if leader is None:
            return Operation(
                op_id=op_id,
                process_id=process_id,
                invoke_ts=invoke_ts,
                complete_ts=time.time(),
                op_type="write",
                key=key,
                input_value=value,
                output_value=None,
                error="NO_LEADER",
                timeout_marker=False,
                node_seen=None,
                fault_epoch=self._fault_epoch,
            )

        success = leader.write(key, value)
        self._replicate()
        return Operation(
            op_id=op_id,
            process_id=process_id,
            invoke_ts=invoke_ts,
            complete_ts=time.time(),
            op_type="write",
            key=key,
            input_value=value,
            output_value="ok" if success else None,
            error=None if success else "WRITE_FAILED",
            timeout_marker=False,
            node_seen=leader.node_id if success else None,
            fault_epoch=self._fault_epoch,
        )

    def read(self, key: str, node_id: Optional[str] = None, process_id: str = "client-0") -> Operation:
        self._op_counter += 1
        op_id = f"op-{self._op_counter}"
        invoke_ts = time.time()

        target_node = self.nodes.get(node_id) if node_id else self.leader
        if target_node is None or not target_node.is_available():
            return Operation(
                op_id=op_id,
                process_id=process_id,
                invoke_ts=invoke_ts,
                complete_ts=time.time(),
                op_type="read",
                key=key,
                input_value=None,
                output_value=None,
                error="NODE_UNAVAILABLE",
                timeout_marker=False,
                node_seen=None,
                fault_epoch=self._fault_epoch,
            )

        ok, value = target_node.read(key)
        return Operation(
            op_id=op_id,
            process_id=process_id,
            invoke_ts=invoke_ts,
            complete_ts=time.time(),
            op_type="read",
            key=key,
            input_value=None,
            output_value=value,
            error=None if ok else "READ_FAILED",
            timeout_marker=False,
            node_seen=target_node.node_id if ok else None,
            fault_epoch=self._fault_epoch,
        )

    def _elect_new_leader(self) -> None:
        candidates = [
            nid for nid, n in self.nodes.items()
            if n.state == NodeState.FOLLOWER
        ]
        if candidates:
            new_leader_id = self._rng.choice(candidates)
            self._leader_id = new_leader_id
            self.nodes[new_leader_id].state = NodeState.LEADER

    def _replicate(self) -> None:
        leader = self.leader
        if leader is None:
            return
        for node in self.nodes.values():
            if node.state == NodeState.FOLLOWER:
                node.apply_replication(leader.log)
