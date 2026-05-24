"""
10-state verdict taxonomy for distributed system test runs.

Three-valued PASS/FAIL/INCONCLUSIVE collapses distinctions that matter:
a clean oracle over a fault-free run is not the same as a linearizability
checker consuming a full history under a proven nemesis.
"""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class Verdict(Enum):
    PASS_SMOKE = "PASS-smoke"
    PASS_HARDENING = "PASS-hardening"
    FAIL_REPRODUCIBLE = "FAIL-reproducible"
    FAIL_NONDETERMINISTIC = "FAIL-nondeterministic"
    INCONCLUSIVE_ENV = "INCONCLUSIVE-env"
    INCONCLUSIVE_ORACLE_TOO_WEAK = "INCONCLUSIVE-oracle-too-weak"
    INCONCLUSIVE_FAULT_NOT_PROVEN = "INCONCLUSIVE-fault-not-proven"
    PARTIAL_SURFACE = "PARTIAL-surface"
    PARTIAL_MODEL = "PARTIAL-model"
    NOT_RUN = "NOT-RUN"

    @property
    def is_pass(self) -> bool:
        return self in {Verdict.PASS_SMOKE, Verdict.PASS_HARDENING}

    @property
    def is_fail(self) -> bool:
        return self in {Verdict.FAIL_REPRODUCIBLE, Verdict.FAIL_NONDETERMINISTIC}

    @property
    def is_inconclusive(self) -> bool:
        return self in {
            Verdict.INCONCLUSIVE_ENV,
            Verdict.INCONCLUSIVE_ORACLE_TOO_WEAK,
            Verdict.INCONCLUSIVE_FAULT_NOT_PROVEN,
        }

    @property
    def is_partial(self) -> bool:
        return self in {Verdict.PARTIAL_SURFACE, Verdict.PARTIAL_MODEL}

    def downgrades_aggregate(self) -> bool:
        """True if this arm verdict caps a scenario-level aggregate at PARTIAL-surface."""
        return self in {Verdict.NOT_RUN, Verdict.PARTIAL_SURFACE, Verdict.PARTIAL_MODEL}


@dataclass
class VerdictDecisionTree:
    """
    Implements the 10-state decision tree from verdict-taxonomy.md.

    Inputs mirror the observable signals a test runner collects during execution.
    """

    attempted: bool
    fault_planned: bool
    fault_proven_landed: bool
    checker_ran: bool
    history_fields_complete: bool
    checker_covered_all_ops: bool
    violation_found: bool
    reproducer_obtained: bool
    env_capability_missing: bool
    serious_scenario: bool

    def evaluate(self) -> Verdict:
        if not self.attempted:
            return Verdict.NOT_RUN

        if self.env_capability_missing:
            return Verdict.INCONCLUSIVE_ENV

        if self.violation_found:
            if self.reproducer_obtained:
                return Verdict.FAIL_REPRODUCIBLE
            return Verdict.FAIL_NONDETERMINISTIC

        if self.fault_planned and not self.fault_proven_landed:
            return Verdict.INCONCLUSIVE_FAULT_NOT_PROVEN

        if self.serious_scenario:
            if not self.checker_ran:
                return Verdict.PARTIAL_SURFACE
            if not self.history_fields_complete:
                return Verdict.INCONCLUSIVE_ORACLE_TOO_WEAK
            if not self.checker_covered_all_ops:
                return Verdict.PARTIAL_MODEL

        if self.fault_planned and self.fault_proven_landed:
            return Verdict.PASS_HARDENING

        return Verdict.PASS_SMOKE


def aggregate_arm_verdicts(arm_verdicts: list[Verdict]) -> Verdict:
    """
    Compute scenario-level aggregate verdict from per-arm verdicts.

    Any NOT-RUN or PARTIAL-* arm caps the aggregate at PARTIAL-surface.
    Any FAIL takes precedence over everything.
    """
    if not arm_verdicts:
        return Verdict.NOT_RUN

    for v in arm_verdicts:
        if v.is_fail:
            return v

    if any(v.downgrades_aggregate() for v in arm_verdicts):
        return Verdict.PARTIAL_SURFACE

    if all(v == Verdict.PASS_HARDENING for v in arm_verdicts):
        return Verdict.PASS_HARDENING

    if all(v.is_pass for v in arm_verdicts):
        return Verdict.PASS_SMOKE

    if any(v.is_inconclusive for v in arm_verdicts):
        return Verdict.INCONCLUSIVE_ENV

    return Verdict.PARTIAL_SURFACE


def session_level_verdict(scenario_verdicts: list[Verdict]) -> str:
    """
    Compute session-level summary from per-scenario verdicts.

    Returns one of: FAIL / DONE_WITH_CONCERNS / DONE / INCONCLUSIVE / BLOCKED
    """
    if not scenario_verdicts:
        return "BLOCKED"

    if any(v.is_fail for v in scenario_verdicts):
        return "FAIL"

    has_pass = any(v.is_pass for v in scenario_verdicts)
    has_inconclusive = any(v.is_inconclusive or v.is_partial or v == Verdict.NOT_RUN for v in scenario_verdicts)

    if has_pass and has_inconclusive:
        return "DONE_WITH_CONCERNS"

    if has_pass:
        return "DONE"

    return "INCONCLUSIVE"
