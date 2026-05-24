"""
Technical debt scorer for EA360 architecture elements.

Assigns P0-P3 priority scores to TOGAF compliance issues and
generates a prioritised refactoring roadmap.

Priority scale:
    P0 — Blocking: violates mandatory TOGAF constraint, blocks validation
    P1 — Critical: significant compliance gap, must fix within one cycle
    P2 — Moderate: best-practice deviation, fix within six months
    P3 — Low: cosmetic or optional enrichment
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class Priority(str):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


# Keyword patterns → priority mapping (order matters: first match wins)
_RULES: list[tuple[str, str, str]] = [
    # (substring_in_warning, priority, remediation_hint)
    ("missing required property", Priority.P0,
     "Add the mandatory TOGAF property before validation."),
    ("no stakeholder", Priority.P1,
     "Assign at least one stakeholder owner per TOGAF ADM Phase A."),
    ("deprecated", Priority.P2,
     "Schedule migration or archival within the current ADM cycle."),
    ("no description", Priority.P3,
     "Add a human-readable description for documentation export."),
]

_DEFAULT = (Priority.P2, "Review against TOGAF 10 Architecture Content Framework.")


@dataclass
class DebtItem:
    element_id: str
    element_name: str
    warning: str
    priority: str
    remediation: str


def score(validation_issues: dict[str, list[str]], elements: dict[str, Any]) -> list[DebtItem]:
    """
    Convert validate_togaf() output into a prioritised debt backlog.

    USE WHEN: After calling validate_togaf() on the EA360 model to
    translate raw TOGAF warnings into an actionable P0-P3 refactoring
    roadmap for architecture governance reviews.

    NEVER USE FOR: Elements that are already archived — debt on archived
    elements is expected and should not pollute the active backlog.

    Args:
        validation_issues: Dict from validate_togaf(), mapping element_id
            to list of TOGAF compliance warning strings.
        elements: Dict mapping element_id → element metadata (must include
            at least "name" and "lifecycle" keys).

    Returns:
        list[DebtItem]: Sorted by priority (P0 first), each item containing
            element_id, element_name, warning, priority, and remediation hint.
    """
    items: list[DebtItem] = []
    for eid, warnings in validation_issues.items():
        elem = elements.get(eid, {})
        if elem.get("lifecycle") == "archived":
            continue
        name = elem.get("name", eid)
        for warning in warnings:
            lower = warning.lower()
            priority, remediation = _DEFAULT
            for keyword, prio, hint in _RULES:
                if keyword in lower:
                    priority, remediation = prio, hint
                    break
            items.append(DebtItem(
                element_id=eid,
                element_name=name,
                warning=warning,
                priority=priority,
                remediation=remediation,
            ))
    _PRIORITY_ORDER = {Priority.P0: 0, Priority.P1: 1, Priority.P2: 2, Priority.P3: 3}
    items.sort(key=lambda x: _PRIORITY_ORDER.get(x.priority, 99))
    return items


def roadmap(items: list[DebtItem]) -> str:
    """
    Render a prioritised refactoring roadmap as Markdown.

    USE WHEN: Preparing a governance report or ADM Phase H (Architecture
    Change Management) deliverable. Suitable for direct inclusion in
    report.md or as input for stakeholder review.

    NEVER USE FOR: Real-time agent feedback — use the raw DebtItem list
    for programmatic processing; this function is for human-readable output.

    Args:
        items: List of DebtItem instances from score().

    Returns:
        str: Markdown-formatted roadmap grouped by priority level.
    """
    if not items:
        return "No technical debt identified. Model is TOGAF compliant."

    sections: dict[str, list[DebtItem]] = {}
    for item in items:
        sections.setdefault(item.priority, []).append(item)

    lines = ["# EA360 Technical Debt Roadmap\n"]
    labels = {
        Priority.P0: "P0 — Blocking (fix immediately)",
        Priority.P1: "P1 — Critical (fix this cycle)",
        Priority.P2: "P2 — Moderate (fix within 6 months)",
        Priority.P3: "P3 — Low (next opportunity)",
    }
    for prio in [Priority.P0, Priority.P1, Priority.P2, Priority.P3]:
        group = sections.get(prio, [])
        if not group:
            continue
        lines.append(f"## {labels[prio]}\n")
        for item in group:
            lines.append(f"- **{item.element_name}**: {item.warning}")
            lines.append(f"  - *Remediation*: {item.remediation}")
        lines.append("")
    return "\n".join(lines)
