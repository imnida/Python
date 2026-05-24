"""
Confidence score propagation for EA360.

Each architecture element carries a base confidence score (0.0–1.0)
representing the certainty of its definition (source quality, stakeholder
validation, data lineage).  This module propagates that score along
ArchiMate relationship chains: a downstream element cannot be more
confident than its least-confident upstream dependency.

Propagation rule (conservative / worst-path):
    confidence(target) = min(confidence(source), confidence(target)) * decay
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DECAY = 0.95  # confidence loss per hop — configurable per governance policy


@dataclass
class ConfidenceNode:
    element_id: str
    element_name: str
    base_score: float
    propagated_score: float = field(init=False)
    limiting_dependency: str | None = None

    def __post_init__(self) -> None:
        self.propagated_score = self.base_score


def propagate(
    elements: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    base_scores: dict[str, float] | None = None,
) -> dict[str, ConfidenceNode]:
    """
    Propagate confidence scores along ArchiMate dependency chains.

    USE WHEN: Assessing the trustworthiness of derived or composed
    architecture elements in the EA360 model. Run this after adding
    new elements or relationships, especially for DataObject chains
    involving confidential data (TOGAF Information Systems Architecture).

    NEVER USE FOR: Elements in 'draft' lifecycle — base scores for
    draft elements are unreliable; set their base_score to 0.5 max
    before running propagation.

    Args:
        elements: List of element dicts (must include "id" and "name").
        relationships: List of relationship dicts (must include "source",
            "target", and "type").
        base_scores: Optional mapping of element_id → initial confidence
            (0.0–1.0). Defaults to 1.0 for all elements if not provided.

    Returns:
        dict: Maps element_id → ConfidenceNode with propagated_score
            and the name of the limiting upstream dependency (if any).
    """
    scores = base_scores or {}
    nodes: dict[str, ConfidenceNode] = {
        e["id"]: ConfidenceNode(
            element_id=e["id"],
            element_name=e["name"],
            base_score=scores.get(e["id"], 1.0),
        )
        for e in elements
    }

    # Simple single-pass propagation (sufficient for DAGs; cycle-safe
    # because ArchiMate models should be acyclic in practice)
    dependency_types = {"realizes", "serves", "used_by", "composed_of", "aggregates"}
    for rel in relationships:
        if rel["type"] not in dependency_types:
            continue
        source = nodes.get(rel["source"])
        target = nodes.get(rel["target"])
        if source is None or target is None:
            continue
        candidate = source.propagated_score * DECAY
        if candidate < target.propagated_score:
            target.propagated_score = candidate
            target.limiting_dependency = source.element_name

    return nodes


def confidence_report(nodes: dict[str, ConfidenceNode], threshold: float = 0.7) -> str:
    """
    Render a Markdown confidence report for elements below threshold.

    USE WHEN: Generating a governance audit report or identifying
    low-confidence chains before an ADM Phase B/C review. Useful as
    input to the authenticity_check module.

    NEVER USE FOR: Passing results to the LLM as raw context — the
    propagated_score dict is more suitable for programmatic use.

    Args:
        nodes: Output of propagate().
        threshold: Score below which an element is flagged (default 0.7).

    Returns:
        str: Markdown report listing elements below threshold with their
            propagated score and limiting dependency name.
    """
    flagged = [n for n in nodes.values() if n.propagated_score < threshold]
    if not flagged:
        return f"All elements meet the confidence threshold (≥ {threshold})."

    flagged.sort(key=lambda n: n.propagated_score)
    lines = [f"# EA360 Confidence Report (threshold: {threshold})\n"]
    for node in flagged:
        dep = f" ← limited by **{node.limiting_dependency}**" if node.limiting_dependency else ""
        lines.append(
            f"- **{node.element_name}**: {node.propagated_score:.2f}{dep}"
        )
    return "\n".join(lines)
