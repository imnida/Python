# Copyright (c) Microsoft Corporation. Licensed under the MIT License.
"""
Agent Governance Toolkit — Python Demo
=======================================

Demonstrates runtime governance for AI agents using the Microsoft
Agent Governance Toolkit (https://github.com/microsoft/agent-governance-toolkit).

Covers four governance patterns relevant to ML/data science workflows:
  1. Lite API  — zero-config allow/deny in 3 lines
  2. Policy Engine — declarative YAML-driven rules
  3. Content Filtering — PII detection in agent outputs
  4. Retrofit Governance — wrapping existing code with no refactor

Run:
    pip install agent-os-kernel agentmesh-platform pydantic pyyaml
    python AgentGovernance/agent_governance_demo.py
"""

from __future__ import annotations

import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Lightweight self-contained governance primitives
# (mirrors agent_os.lite / agent_os.policies so the demo runs offline)
# ---------------------------------------------------------------------------

class GovernanceViolation(Exception):
    def __init__(self, action: str, reason: str) -> None:
        self.action = action
        self.reason = reason
        super().__init__(f"Governance violation: '{action}' — {reason}")


@dataclass
class Decision:
    action: str
    allowed: bool
    reason: str
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        icon = "✅" if self.allowed else "🚫"
        return f"{icon} {self.action:<30} {self.reason:<50} ({self.latency_ms:.3f}ms)"


class LiteGovernor:
    """Mirrors `agent_os.lite.govern` — single-import, zero-config governance."""

    def __init__(
        self,
        allow: list[str] | None = None,
        deny: list[str] | None = None,
        deny_patterns: list[str] | None = None,
        blocked_content: list[str] | None = None,
        max_calls: int = 0,
    ) -> None:
        self._allow = set(allow) if allow else None
        self._deny = set(deny or [])
        self._deny_patterns = [re.compile(p, re.IGNORECASE) for p in (deny_patterns or [])]
        self._blocked_content = [re.compile(p, re.IGNORECASE) for p in (blocked_content or [])]
        self._max_calls = max_calls
        self._call_count = 0
        self._audit: list[Decision] = []

    def __call__(self, action: str, content: str = "") -> bool:
        decision = self.evaluate(action, content)
        if not decision.allowed:
            raise GovernanceViolation(action, decision.reason)
        return True

    def is_allowed(self, action: str, content: str = "") -> bool:
        return self.evaluate(action, content).allowed

    def evaluate(self, action: str, content: str = "") -> Decision:
        start = time.perf_counter()

        if self._max_calls > 0:
            self._call_count += 1
            if self._call_count > self._max_calls:
                return self._decide(action, False, f"Rate limit exceeded ({self._max_calls} max)", start)

        if action in self._deny:
            return self._decide(action, False, f"'{action}' is explicitly denied", start)

        for pat in self._deny_patterns:
            if pat.search(action):
                return self._decide(action, False, f"'{action}' matches deny pattern", start)

        if content:
            for pat in self._blocked_content:
                if pat.search(content):
                    return self._decide(action, False, "Content matches blocked PII pattern", start)

        if self._allow is not None and action not in self._allow:
            return self._decide(action, False, f"'{action}' not in allow list", start)

        return self._decide(action, True, "Allowed by policy", start)

    @property
    def stats(self) -> dict[str, Any]:
        total = len(self._audit)
        denied = sum(1 for d in self._audit if not d.allowed)
        avg_ms = sum(d.latency_ms for d in self._audit) / total if total else 0
        return {
            "total": total,
            "allowed": total - denied,
            "denied": denied,
            "violation_rate": f"{denied / total * 100:.1f}%" if total else "0.0%",
            "avg_latency_ms": f"{avg_ms:.4f}",
        }

    def _decide(self, action: str, allowed: bool, reason: str, start: float) -> Decision:
        d = Decision(action, allowed, reason, (time.perf_counter() - start) * 1000)
        self._audit.append(d)
        return d


def govern(
    allow: list[str] | None = None,
    deny: list[str] | None = None,
    deny_patterns: list[str] | None = None,
    blocked_content: list[str] | None = None,
    max_calls: int = 0,
) -> LiteGovernor:
    """Create a lightweight governance gate — mirrors ``agent_os.lite.govern``."""
    return LiteGovernor(
        allow=allow,
        deny=deny,
        deny_patterns=deny_patterns,
        blocked_content=blocked_content,
        max_calls=max_calls,
    )


# ---------------------------------------------------------------------------
# Minimal PolicyEvaluator (mirrors agent_os.policies.PolicyEvaluator)
# ---------------------------------------------------------------------------

@dataclass
class PolicyRule:
    name: str
    field: str
    operator: str        # "in", "not_in", "eq", "gt", "lt", "matches"
    value: Any
    action: str          # "allow" | "deny"
    priority: int = 0
    message: str = ""


@dataclass
class PolicyDocument:
    name: str
    version: str
    rules: list[PolicyRule]
    default_action: str = "allow"

    @staticmethod
    def from_yaml(path: str) -> "PolicyDocument":
        """Load a PolicyDocument from a YAML file."""
        import yaml  # optional — only needed for YAML loading
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        rules = []
        for r in data.get("rules", []):
            cond = r["condition"]
            rules.append(PolicyRule(
                name=r["name"],
                field=cond["field"],
                operator=cond["operator"],
                value=cond["value"],
                action=r["action"],
                priority=r.get("priority", 0),
                message=r.get("message", ""),
            ))
        rules.sort(key=lambda r: r.priority, reverse=True)
        return PolicyDocument(
            name=data.get("name", "unnamed"),
            version=data.get("version", "1.0"),
            rules=rules,
            default_action=data.get("defaults", {}).get("action", "allow"),
        )


class PolicyEvaluator:
    """Deterministic policy evaluator — mirrors ``agent_os.policies.PolicyEvaluator``."""

    def __init__(self, document: PolicyDocument) -> None:
        self._doc = document
        self._audit: list[Decision] = []

    def evaluate(self, context: dict[str, Any]) -> Decision:
        start = time.perf_counter()
        action_name = context.get("tool_name", context.get("action", "unknown"))

        for rule in self._doc.rules:
            field_val = context.get(rule.field)
            if field_val is None:
                continue
            if self._match(rule, field_val):
                allowed = rule.action == "allow"
                reason = rule.message or f"Rule '{rule.name}' matched"
                d = Decision(action_name, allowed, reason, (time.perf_counter() - start) * 1000)
                self._audit.append(d)
                return d

        allowed = self._doc.default_action == "allow"
        d = Decision(
            action_name, allowed,
            f"Default policy action: {self._doc.default_action}",
            (time.perf_counter() - start) * 1000,
        )
        self._audit.append(d)
        return d

    def _match(self, rule: PolicyRule, field_val: Any) -> bool:
        op = rule.operator
        v = rule.value
        if op == "in":
            return field_val in v
        if op == "not_in":
            return field_val not in v
        if op == "eq":
            return field_val == v
        if op == "gt":
            return isinstance(field_val, (int, float)) and field_val > v
        if op == "lt":
            return isinstance(field_val, (int, float)) and field_val < v
        if op == "gte":
            return isinstance(field_val, (int, float)) and field_val >= v
        if op == "lte":
            return isinstance(field_val, (int, float)) and field_val <= v
        if op == "matches":
            return bool(re.search(v, str(field_val), re.IGNORECASE))
        if op == "contains":
            return v in str(field_val)
        return False

    @property
    def audit(self) -> list[Decision]:
        return list(self._audit)


# ---------------------------------------------------------------------------
# Demo sections
# ---------------------------------------------------------------------------

SEPARATOR = "─" * 65


def section(title: str) -> None:
    print(f"\n{'═' * 65}")
    print(f"  {title}")
    print('═' * 65)


def show(decision: Decision) -> None:
    print(f"  {decision}")


# ── 1. Lite API ──────────────────────────────────────────────────────────

def demo_lite_api() -> None:
    section("1. Lite API — Zero-config governance in 3 lines")

    # 3 lines to add governance to any agent:
    check = govern(
        allow=["read_csv", "load_dataset", "predict", "classify",
               "generate_embedding", "query_database_readonly",
               "fetch_model_metrics", "score_model"],
        deny=["delete_file", "overwrite_dataset", "execute_shell",
              "drop_table", "send_email"],
    )

    actions = [
        "read_csv",
        "load_dataset",
        "predict",
        "execute_shell",
        "delete_file",
        "generate_embedding",
        "drop_table",
        "score_model",
        "send_email",
    ]
    print(f"\n  Policy: allowlist={len(check._allow)} tools, denylist={len(check._deny)} tools\n")
    for action in actions:
        show(check.evaluate(action))

    stats = check.stats
    print(f"\n  {SEPARATOR}")
    print(f"  Total: {stats['total']} | Allowed: {stats['allowed']} | "
          f"Denied: {stats['denied']} | Violation rate: {stats['violation_rate']} | "
          f"Avg latency: {stats['avg_latency_ms']}ms")


# ── 2. YAML Policy Engine ────────────────────────────────────────────────

def demo_policy_engine() -> None:
    section("2. Policy Engine — Declarative YAML-driven rules")

    policy_path = Path(__file__).parent / "policies" / "data_science_policy.yaml"
    try:
        doc = PolicyDocument.from_yaml(str(policy_path))
    except ImportError:
        print("  ⚠  PyYAML not installed — skipping YAML demo. Run: pip install pyyaml")
        return

    evaluator = PolicyEvaluator(doc)

    test_contexts = [
        {"tool_name": "read_csv",            "description": "Load training data"},
        {"tool_name": "predict",             "description": "Run model inference"},
        {"tool_name": "query_database_readonly", "description": "Read SQL results"},
        {"tool_name": "delete_file",         "description": "Delete a dataset file"},
        {"tool_name": "drop_table",          "description": "Drop a database table"},
        {"tool_name": "execute_shell",       "description": "Arbitrary shell command"},
        {"tool_name": "send_email",          "description": "Export data via email"},
        {"tool_name": "score_model",         "description": "Score ML model"},
        {"tool_name": "token_count",         "token_count": 150000,
         "description": "Oversized token request"},
        {"tool_name": "run_inference",       "description": "Approved inference tool"},
    ]

    print(f"\n  Loaded policy: '{doc.name}' v{doc.version} ({len(doc.rules)} rules)\n")
    for ctx in test_contexts:
        desc = ctx.pop("description")
        decision = evaluator.evaluate(ctx)
        ctx["description"] = desc  # restore for readability
        label = f"{ctx.get('tool_name', '?')}"
        icon = "✅" if decision.allowed else "🚫"
        print(f"  {icon} {label:<35} {decision.reason[:45]}")

    print(f"\n  Total evaluations: {len(evaluator.audit)}")


# ── 3. Content Filtering (PII Detection) ────────────────────────────────

def demo_content_filtering() -> None:
    section("3. Content Filtering — PII detection in agent outputs")

    PII_PATTERNS = [
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",  # email
        r"(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",  # phone
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"(?:api[_-]?key|secret[_-]?key|bearer)[\s:=]+['\"]?[A-Za-z0-9_\-]{16,}['\"]?",  # API key
    ]

    check = govern(
        allow=["export_results", "write_report", "log_metrics"],
        blocked_content=PII_PATTERNS,
    )

    test_outputs = [
        ("export_results", "Model accuracy: 94.2%, F1: 0.91, AUC: 0.97"),
        ("write_report",   "Churn rate down 3.2% this quarter. See attached chart."),
        ("log_metrics",    "Loss: 0.032, Val-loss: 0.041, Epoch: 42"),
        ("export_results", "Customer john.doe@example.com has churn probability 0.87"),
        ("write_report",   "Contact support at 555-867-5309 for data access requests"),
        ("export_results", "User SSN 123-45-6789 — churn score: 0.92"),
        ("log_metrics",    "API_KEY=sk-abcdefghijklmnop1234567890 — model loaded"),
    ]

    print(f"\n  PII patterns active: {len(PII_PATTERNS)} (email, phone, SSN, API key)\n")
    for action, content in test_outputs:
        decision = check.evaluate(action, content)
        icon = "✅" if decision.allowed else "🛡️ "
        preview = content[:55] + ("…" if len(content) > 55 else "")
        print(f"  {icon} {action:<20} │ {preview}")
        if not decision.allowed:
            print(f"       └─ BLOCKED: {decision.reason}")

    stats = check.stats
    print(f"\n  Blocked {stats['denied']}/{stats['total']} outputs — "
          f"{stats['violation_rate']} violation rate")


# ── 4. Retrofit Governance ───────────────────────────────────────────────

def demo_retrofit_governance() -> None:
    section("4. Retrofit Governance — Wrapping existing code, zero refactor")

    # ── Existing code (unchanged) ────────────────────────────────────────
    def run_ml_pipeline(query: str) -> str:
        """Your existing ML pipeline — no changes needed."""
        return f"Pipeline result for: {query!r}"

    # ── Governance wrapper (the only new code) ───────────────────────────
    BLOCKED = ["DROP TABLE", "rm -rf", "os.system", "subprocess", "DELETE FROM"]
    check = govern(blocked_content=[re.escape(p) for p in BLOCKED], max_calls=20)
    audit_log: list[dict[str, Any]] = []

    def governed_pipeline(query: str) -> str | None:
        """Drop-in replacement — policy-checks before delegating."""
        decision = check.evaluate("run_pipeline", content=query)
        audit_log.append({
            "ts": datetime.now(timezone.utc).isoformat(),
            "query_preview": query[:60],
            "allowed": decision.allowed,
            "reason": decision.reason,
        })
        if not decision.allowed:
            print(f"  🚫 BLOCKED  │ {query[:60]!r}")
            print(f"       └─ {decision.reason}")
            return None
        result = run_ml_pipeline(query)
        print(f"  ✅ ALLOWED  │ {query[:60]!r}")
        return result

    # ── Test it ──────────────────────────────────────────────────────────
    queries = [
        "Predict customer churn for Q3 2024",
        "Summarize sentiment from last week's reviews",
        "DROP TABLE customer_data; --",
        "Analyze portfolio returns over the past year",
        "rm -rf /data/training_sets",
        "Load the LSTM model and forecast next 30 days",
        "subprocess.call(['curl', 'malicious.com'])",
        "Calculate F1 score for the classification model",
    ]

    print(f"\n  Blocked patterns: {BLOCKED}\n")
    for query in queries:
        governed_pipeline(query)

    print(f"\n  {SEPARATOR}")
    print(f"  Audit trail: {len(audit_log)} entries logged")
    blocked = sum(1 for e in audit_log if not e["allowed"])
    print(f"  Blocked: {blocked}/{len(audit_log)} queries "
          f"({blocked/len(audit_log)*100:.0f}% rejection rate)")

    print(f"\n  Sample audit entries:")
    for entry in audit_log[:3]:
        status = "BLOCKED" if not entry["allowed"] else "ALLOWED"
        print(f"    [{entry['ts'][:19]}] {status:<8} {entry['query_preview']!r:.55s}")


# ── 5. Rate Limiting ─────────────────────────────────────────────────────

def demo_rate_limiting() -> None:
    section("5. Rate Limiting — Cap agent tool-call volume")

    check = govern(
        allow=["predict", "classify", "embed"],
        max_calls=5,
    )

    print(f"\n  Rate limit: 5 calls max\n")
    for i in range(8):
        action = ["predict", "classify", "embed"][i % 3]
        decision = check.evaluate(action)
        icon = "✅" if decision.allowed else "⛔"
        print(f"  Call {i + 1:>2}: {icon} {action:<12} {decision.reason}")

    stats = check.stats
    print(f"\n  Stats: {stats['total']} calls, {stats['denied']} rate-limited "
          f"({stats['violation_rate']} violation rate)")


# ── Summary ──────────────────────────────────────────────────────────────

def print_summary() -> None:
    print(f"\n{'═' * 65}")
    print("  SUMMARY — Agent Governance Toolkit")
    print('═' * 65)
    print("""
  Pattern                  What it does
  ─────────────────────── ────────────────────────────────────────────
  Lite API                 3-line allow/deny enforcement, audit trail
  Policy Engine            Declarative YAML rules, priority ordering
  Content Filtering        PII detection blocks sensitive output
  Retrofit Governance      Wrap existing code with no refactor
  Rate Limiting            Cap agent tool-call volume

  Key properties (from AGT benchmarks):
    • Sub-millisecond latency: < 0.1ms p99 governance pipeline
    • Zero false negatives:    0.00% policy violation rate (vs 26.67%
                               for prompt-based "please follow rules")
    • Fail-closed:             Engine errors → action denied
    • Tamper-evident:          Merkle-chained audit logs (full stack)

  Install:   pip install agent-governance-toolkit[full]
  Docs:      https://github.com/microsoft/agent-governance-toolkit
""")


# ── Entry point ──────────────────────────────────────────────────────────

def main() -> None:
    print("\n🛡️  Microsoft Agent Governance Toolkit — Python Demo")
    print(f"   Running self-contained governance primitives (no install required)\n")

    demo_lite_api()
    demo_policy_engine()
    demo_content_filtering()
    demo_retrofit_governance()
    demo_rate_limiting()
    print_summary()


if __name__ == "__main__":
    main()
