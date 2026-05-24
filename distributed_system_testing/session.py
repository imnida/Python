"""
Test session management for distributed system test runs.

A session ties together a plan, a set of scenarios, and the raw artifacts
produced during execution. Each scenario is run in plan order; results are
written incrementally so partial findings survive a session timeout.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from .claims import Claim
from .faults import LandingEvidence, Nemesis
from .oracles import Oracle, OracleResult
from .simulator import OperationHistory
from .verdicts import Verdict, VerdictDecisionTree


@dataclass
class BudgetTier:
    """Minimum configuration required to claim a given PASS tier."""
    node_count: int
    duration_seconds: float
    fault_count: int
    seed_count: int
    description: str = ""


@dataclass
class ScenarioBudgets:
    smoke: BudgetTier
    hardening: BudgetTier
    release: Optional[BudgetTier] = None
    release_not_provided_reason: str = ""

    @property
    def has_release_budget(self) -> bool:
        return self.release is not None


@dataclass
class Scenario:
    id: str
    name: str
    falsifies_claims: list[Claim]
    hypothesis_ids: list[str]
    technique: str
    workload_description: str
    faults_description: str
    oracle: Oracle
    nemesis: Optional[Nemesis]
    budgets: ScenarioBudgets
    target_test_file: str = ""
    serious: bool = False

    @property
    def claim_ids(self) -> list[str]:
        return [c.id for c in self.falsifies_claims]


@dataclass
class ScenarioResult:
    scenario: Scenario
    verdict: Verdict
    oracle_result: Optional[OracleResult]
    landing_evidence: Optional[LandingEvidence]
    history: Optional[OperationHistory]
    elapsed_seconds: float
    budget_tier_met: str
    notes: str = ""
    anomalies: list[str] = field(default_factory=list)

    def to_markdown_row(self) -> str:
        oracle_summary = "n/a"
        if self.oracle_result:
            count = self.oracle_result.ops_consumed
            anomaly_count = self.oracle_result.anomaly_count
            oracle_summary = f"{count} ops, {anomaly_count} anomalies"

        fault_proven = "yes" if (self.landing_evidence and self.landing_evidence.proven) else "no"
        return (
            f"| {self.scenario.id} | {self.scenario.name} | {self.verdict.value} "
            f"| {oracle_summary} | fault landed: {fault_proven} | {self.budget_tier_met} |"
        )


class TestSession:
    """
    Drives scenario execution in plan order, recording results incrementally.
    """

    def __init__(
        self,
        plan_slug: str,
        session_root: Path = Path("test-sessions"),
    ) -> None:
        self.plan_slug = plan_slug
        self._ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        self.session_dir = session_root / plan_slug / self._ts
        self.session_dir.mkdir(parents=True, exist_ok=True)
        (self.session_dir / "logs").mkdir(exist_ok=True)
        (self.session_dir / "metrics").mkdir(exist_ok=True)
        (self.session_dir / "artifacts").mkdir(exist_ok=True)
        (self.session_dir / "findings").mkdir(exist_ok=True)
        self._results: list[ScenarioResult] = []
        self._log_path = self.session_dir / "session-log.md"
        self._write_log_header()

    def run_scenario(
        self,
        scenario: Scenario,
        runner: Callable[[Scenario], ScenarioResult],
    ) -> ScenarioResult:
        self._log(f"Starting scenario {scenario.id}: {scenario.name}")
        start = time.time()

        result = runner(scenario)

        elapsed = time.time() - start
        self._log(
            f"Scenario {scenario.id} finished in {elapsed:.1f}s — verdict: {result.verdict.value}"
        )
        self._results.append(result)
        self._write_incremental_finding(result)
        return result

    def results(self) -> list[ScenarioResult]:
        return list(self._results)

    def _write_log_header(self) -> None:
        content = f"""# Session Log: {self.plan_slug}

**UTC timestamp:** {self._ts}
**Session directory:** {self.session_dir}

## Timeline

"""
        self._log_path.write_text(content)

    def _log(self, message: str) -> None:
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._log_path.open("a") as f:
            f.write(f"- `{ts}` {message}\n")

    def _write_incremental_finding(self, result: ScenarioResult) -> None:
        path = self.session_dir / "findings" / f"{result.scenario.id}.md"
        oracle_text = "n/a"
        if result.oracle_result:
            oracle_text = result.oracle_result.summary()

        evidence_text = "none"
        if result.landing_evidence:
            evidence_text = result.landing_evidence.signal

        content = f"""# Finding: {result.scenario.id} — {result.scenario.name}

**Verdict:** {result.verdict.value}
**Budget tier met:** {result.budget_tier_met}
**Elapsed:** {result.elapsed_seconds:.1f}s
**Claims falsified if FAIL:** {', '.join(result.scenario.claim_ids)}

## Oracle execution evidence

{oracle_text}

## Nemesis landing evidence

{evidence_text}

## Notes

{result.notes or 'none'}
"""
        path.write_text(content)
