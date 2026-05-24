"""
Findings report generation for distributed system test sessions.

The report closes the adequacy loop: plan §7b argued what the scenarios would
falsify; this report shows what actually ran, what the verdicts were, and what
the adequacy assessment is after the run.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .claims import Claim
from .session import ScenarioResult
from .verdicts import Verdict, session_level_verdict


class BlameCategory(Enum):
    """Orthogonal to verdict — classifies which component holds the bug."""
    SUT = "SUT"
    HARNESS = "harness"
    CHECKER = "checker"
    ENVIRONMENT = "environment"
    UNKNOWN = "unknown"


class TaxDCType(Enum):
    """TaxDC-derived bug type (Leesatapornwongsa et al., ASPLOS'16)."""
    TIMING = "timing"
    ORDERING = "ordering"
    PARTITION = "partition"
    CRASH_RECOVERY = "crash-recovery"
    UPGRADE = "upgrade"
    CONFIG = "config"
    FAULT_HANDLING = "fault-handling"
    PERFORMANCE = "performance"


@dataclass
class Finding:
    """A confirmed failure with blame and TaxDC classification."""

    finding_id: str
    scenario_id: str
    verdict: Verdict
    blame: BlameCategory
    taxdc_type: TaxDCType
    severity: str
    description: str
    reproducer: str
    suggested_action: str
    secondary_tags: list[str] = field(default_factory=list)

    def to_markdown(self) -> str:
        tags = ", ".join(self.secondary_tags) if self.secondary_tags else "none"
        return f"""### {self.finding_id} — {self.verdict.value}

**Scenario:** {self.scenario_id}
**Blame:** {self.blame.value}
**TaxDC type:** {self.taxdc_type.value}
**Secondary tags:** {tags}
**Severity:** {self.severity}

**Description:** {self.description}

**Reproducer:** {self.reproducer}

**Suggested action:** {self.suggested_action}
"""


class FindingsReport:
    """
    Structured findings report matching the findings-report-template shape.

    The report must include:
    - Per-scenario verdict table
    - Surface coverage table (if §7.M.S arms exist)
    - Release-budget disclosures
    - Adequacy assessment vs plan
    - Confidence delta
    """

    def __init__(
        self,
        plan_slug: str,
        plan_claims: list[Claim],
        results: list[ScenarioResult],
        findings: Optional[list[Finding]] = None,
    ) -> None:
        self.plan_slug = plan_slug
        self.plan_claims = plan_claims
        self.results = results
        self.findings = findings or []

    @property
    def session_verdict(self) -> str:
        verdicts = [r.verdict for r in self.results]
        return session_level_verdict(verdicts)

    def render(self) -> str:
        parts = [
            self._render_header(),
            self._render_scenario_table(),
            self._render_findings(),
            self._render_release_budget_disclosures(),
            self._render_adequacy_assessment(),
            self._render_confidence_delta(),
        ]
        return "\n\n".join(parts)

    def _render_header(self) -> str:
        fail_count = sum(1 for r in self.results if r.verdict.is_fail)
        pass_count = sum(1 for r in self.results if r.verdict.is_pass)
        inconclusive_count = sum(1 for r in self.results if r.verdict.is_inconclusive or r.verdict.is_partial)

        p0_findings = [f for f in self.findings if f.severity == "P0"]
        critical_section = ""
        if p0_findings:
            descriptions = "\n".join(f.description for f in p0_findings)
            critical_section = f"## Critical findings\n\n{descriptions}"

        return (
            f"# Findings Report: {self.plan_slug}\n\n"
            f"**Session verdict:** {self.session_verdict}\n"
            f"**Scenarios run:** {len(self.results)}\n"
            f"**PASS:** {pass_count} | **FAIL:** {fail_count} | **INCONCLUSIVE/PARTIAL:** {inconclusive_count}\n\n"
            f"{critical_section}\n"
        )

    def _render_scenario_table(self) -> str:
        header = "| Scenario | Name | Verdict | Oracle evidence | Fault proven | Budget tier |"
        sep = "|---|---|---|---|---|---|"
        rows = [r.to_markdown_row() for r in self.results]
        return "## Scenario results\n\n" + "\n".join([header, sep] + rows)

    def _render_findings(self) -> str:
        if not self.findings:
            return "## Findings\n\nNo failures recorded in this session."
        parts = ["## Findings"]
        for finding in self.findings:
            parts.append(finding.to_markdown())
        return "\n\n".join(parts)

    def _render_release_budget_disclosures(self) -> str:
        missing = [
            r for r in self.results
            if not r.scenario.budgets.has_release_budget
        ]
        if not missing:
            return "## Release-budget disclosures\n\nAll scenarios declared a concrete release budget."

        lines = ["## Release-budget disclosures", ""]
        for r in missing:
            reason = r.scenario.budgets.release_not_provided_reason or "not specified"
            lines.append(f"- **{r.scenario.id}** ({r.scenario.name}): {reason}")
        return "\n".join(lines)

    def _render_adequacy_assessment(self) -> str:
        lines = [
            "## Adequacy assessment vs plan",
            "",
            "| Claim | Plan argued | What ran | Adequacy |",
            "|---|---|---|---|",
        ]
        result_by_claim: dict[str, list[ScenarioResult]] = {}
        for r in self.results:
            for cid in r.scenario.claim_ids:
                result_by_claim.setdefault(cid, []).append(r)

        for claim in self.plan_claims:
            ran = result_by_claim.get(claim.id, [])
            if not ran:
                lines.append(f"| {claim.id} | scenarios designed | no scenario ran | **gap** |")
            else:
                verdicts = [r.verdict.value for r in ran]
                has_fail = any(r.verdict.is_fail for r in ran)
                adequacy = "adequate" if not has_fail and ran else "gap" if not ran else "see findings"
                lines.append(f"| {claim.id} | {len(ran)} scenario(s) | {', '.join(verdicts)} | {adequacy} |")

        return "\n".join(lines)

    def _render_confidence_delta(self) -> str:
        has_hardening = any(r.verdict == Verdict.PASS_HARDENING for r in self.results)
        has_fail = any(r.verdict.is_fail for r in self.results)

        if has_fail:
            delta = "LESS — failures were found; do not ship until findings are resolved"
        elif has_hardening:
            delta = "MORE — at least one scenario reached PASS-hardening with landing evidence"
        else:
            delta = "UNCHANGED — no hardening-tier evidence collected; smoke-level confidence only"

        return f"""## Confidence delta

{delta}

The run {"raised" if has_hardening else "did not raise"} the confidence in the claimed guarantees.
{"One or more claims were falsified — see Findings section." if has_fail else ""}
"""
