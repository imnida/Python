"""
Oracle patterns for distributed system test verification.

An oracle is a machine-checkable property applied to an operation history.
"Logs look fine" is not an oracle.

Implements the most common checker patterns from oracle-patterns.md:
- LinearizabilityOracle: checks that operations are consistent with a
  single-copy register under concurrent access.
- MonotonicReadOracle: checks that reads never observe a value older than
  a previous read by the same process.
- IdempotencyOracle: checks that no idempotency key produced two committed effects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional

from .simulator import Operation, OperationHistory


@dataclass
class OracleResult:
    passed: bool
    anomalies: list[str]
    ops_consumed: int
    checker_name: str

    @property
    def anomaly_count(self) -> int:
        return len(self.anomalies)

    def summary(self) -> str:
        status = "PASS" if self.passed else "FAIL"
        lines = [f"{self.checker_name}: {status} ({self.ops_consumed} ops, {self.anomaly_count} anomalies)"]
        for anomaly in self.anomalies[:5]:
            lines.append(f"  - {anomaly}")
        if self.anomaly_count > 5:
            lines.append(f"  ... and {self.anomaly_count - 5} more")
        return "\n".join(lines)


class Oracle(ABC):
    @abstractmethod
    def check(self, history: OperationHistory) -> OracleResult:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    def required_history_fields(self) -> list[str]:
        """Returns the canonical history fields this checker requires."""
        return ["op_id", "process_id", "invoke_ts", "complete_ts", "op_type", "key",
                "input_value", "output_value", "error", "timeout_marker", "node_seen"]


class LinearizabilityOracle(Oracle):
    """
    Checks that each key's operation history is consistent with a single
    linearizable register.

    Uses a simplified sequential consistency check: for each key, completed
    writes must appear in the reads in a total order consistent with real-time
    ordering of operations.

    A full implementation would use the Elle checker or Knossos.
    """

    @property
    def name(self) -> str:
        return "LinearizabilityOracle (register model)"

    def check(self, history: OperationHistory) -> OracleResult:
        if not history.has_required_fields():
            return OracleResult(
                passed=False,
                anomalies=["History missing required fields — cannot run checker"],
                ops_consumed=0,
                checker_name=self.name,
            )

        anomalies: list[str] = []
        ops = history.completed_ops()

        keys = {op.key for op in ops}
        for key in keys:
            key_ops = history.ops_by_key(key)
            anomalies.extend(self._check_key(key, key_ops))

        return OracleResult(
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            ops_consumed=len(ops),
            checker_name=self.name,
        )

    def _check_key(self, key: str, ops: list[Operation]) -> list[str]:
        anomalies: list[str] = []
        writes = [op for op in ops if op.op_type == "write" and op.output_value == "ok"]
        reads = [op for op in ops if op.op_type == "read" and op.error is None]

        write_values_by_time = sorted(
            [(op.complete_ts or op.invoke_ts, op.input_value) for op in writes],
            key=lambda x: x[0],
        )

        latest_written: Any = None
        for ts, val in write_values_by_time:
            latest_written = val

        for read_op in reads:
            if read_op.output_value is None and latest_written is not None:
                pass
            elif latest_written is not None and read_op.output_value != latest_written:
                reads_before_last_write = [
                    op for op in writes
                    if (op.complete_ts or op.invoke_ts) > (read_op.complete_ts or read_op.invoke_ts)
                ]
                if not reads_before_last_write:
                    anomalies.append(
                        f"key={key!r}: read returned {read_op.output_value!r} "
                        f"but latest committed write was {latest_written!r} "
                        f"(op_id={read_op.op_id}, node={read_op.node_seen})"
                    )

        return anomalies


class MonotonicReadOracle(Oracle):
    """
    Checks that a client process never observes a value older than a
    previously observed value (monotonic-read consistency).

    Stale reads from followers that lag behind the leader violate this
    and would be detected here.
    """

    @property
    def name(self) -> str:
        return "MonotonicReadOracle"

    def check(self, history: OperationHistory) -> OracleResult:
        anomalies: list[str] = []
        ops = history.completed_ops()

        process_latest_value: dict[tuple[str, str], Any] = {}

        for op in sorted(ops, key=lambda o: o.invoke_ts):
            if op.op_type != "read" or op.error is not None:
                continue

            pid_key = (op.process_id, op.key)
            prev_val = process_latest_value.get(pid_key)

            if prev_val is not None and op.output_value != prev_val:
                anomalies.append(
                    f"process={op.process_id} key={op.key!r}: "
                    f"read {op.output_value!r} after previously reading {prev_val!r} "
                    f"(possible stale read from node={op.node_seen})"
                )

            if op.output_value is not None:
                process_latest_value[pid_key] = op.output_value

        return OracleResult(
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            ops_consumed=len([o for o in ops if o.op_type == "read"]),
            checker_name=self.name,
        )


class IdempotencyOracle(Oracle):
    """
    Checks that no idempotency key produced two committed effects.

    Detects the class of bug where a retry causes a duplicate write
    that is applied twice on the server side.
    """

    def __init__(self, idempotency_key_field: str = "input_value") -> None:
        self._key_field = idempotency_key_field

    @property
    def name(self) -> str:
        return "IdempotencyOracle"

    def check(self, history: OperationHistory) -> OracleResult:
        anomalies: list[str] = []
        ops = history.completed_ops()

        writes = [op for op in ops if op.op_type == "write" and op.output_value == "ok"]
        seen: dict[Any, list[str]] = {}

        for op in writes:
            ikey = op.input_value
            if ikey in seen:
                anomalies.append(
                    f"Idempotency violation: key={op.key!r} input={ikey!r} "
                    f"committed twice (op_ids: {seen[ikey] + [op.op_id]})"
                )
            else:
                seen[ikey] = [op.op_id]

        return OracleResult(
            passed=len(anomalies) == 0,
            anomalies=anomalies,
            ops_consumed=len(writes),
            checker_name=self.name,
        )
