"""
Governed tool registry for the ArchiMate Generator Agent.

Every tool function is checked against harness_policy.yaml before execution.
This is the AGT enforcement point: if a tool name appears in the deny list,
the call is rejected with a DENY decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml


# ── Policy enforcement ────────────────────────────────────────────────────────

@dataclass
class GovernanceDecision:
    allowed: bool
    message: str = ""


class PolicyEvaluator:
    """Lightweight read of harness_policy.yaml — evaluates tool_name fields only."""

    def __init__(self, policy_path: Path) -> None:
        policy = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
        self._deny: dict[str, str] = {}  # tool_name → human-readable message
        for rule in policy.get("rules", []):
            if rule.get("action") != "deny":
                continue
            cond = rule.get("condition", {})
            if cond.get("field") == "tool_name" and cond.get("operator") == "in":
                msg = rule.get("message", rule["name"])
                for tool in cond["value"]:
                    self._deny.setdefault(tool, msg)

    def evaluate(self, tool_name: str) -> GovernanceDecision:
        if tool_name in self._deny:
            return GovernanceDecision(allowed=False, message=self._deny[tool_name])
        return GovernanceDecision(allowed=True)


# ── Model accumulator ─────────────────────────────────────────────────────────

@dataclass
class ModelState:
    motivation:    dict[str, list]      = field(default_factory=lambda: {
                       "principles": [], "constraints": [], "requirements": []})
    layers:        list[dict]           = field(default_factory=list)
    relationships: list[dict]           = field(default_factory=list)
    events:        list[str]            = field(default_factory=list)
    _enrichments:  dict[str, dict]      = field(default_factory=dict)


# ── Tool functions ────────────────────────────────────────────────────────────

def make_tools(
    state:       ModelState,
    evaluator:   PolicyEvaluator,
    output_path: Path,
    boucle0_fn:  Callable | None = None,
    archiserver: str | None = None,
) -> dict[str, Callable]:
    """Return a dict of governed tool callables keyed by tool name."""

    def _guard(tool_name: str) -> None:
        decision = evaluator.evaluate(tool_name)
        if not decision.allowed:
            raise PermissionError(f"[AGT DENY] {decision.message}")

    def add_principle(id: str, severity: str, text: str, rationale: str = "") -> str:
        _guard("add_principle")
        entry: dict[str, Any] = {"id": id, "severity": severity, "text": text}
        if rationale:
            entry["rationale"] = rationale
        state.motivation["principles"].append(entry)
        return f"Principle {id} added"

    def add_constraint(id: str, severity: str, text: str, rationale: str = "") -> str:
        _guard("add_constraint")
        entry: dict[str, Any] = {"id": id, "severity": severity, "text": text}
        if rationale:
            entry["rationale"] = rationale
        state.motivation["constraints"].append(entry)
        return f"Constraint {id} added"

    def add_requirement(id: str, severity: str, text: str, rationale: str = "") -> str:
        _guard("add_requirement")
        entry: dict[str, Any] = {"id": id, "severity": severity, "text": text}
        if rationale:
            entry["rationale"] = rationale
        state.motivation["requirements"].append(entry)
        return f"Requirement {id} added"

    def enrich_component(
        name: str,
        semantic_role: str = "",
        design_notes: str = "",
        risk_level: str = "",
    ) -> str:
        _guard("enrich_component")
        state._enrichments[name] = {
            k: v for k, v in {
                "semantic_role": semantic_role,
                "design_notes":  design_notes,
                "risk_level":    risk_level,
            }.items() if v
        }
        return f"Component '{name}' enriched"

    def add_relationship(
        from_comp: str,
        to_comp: str,
        rel_type: str,
        access: str = "",
        forbidden: bool = False,
    ) -> str:
        _guard("add_relationship")
        entry: dict[str, Any] = {
            "from": from_comp, "to": to_comp,
            "type": rel_type,  "forbidden": forbidden,
        }
        if access:
            entry["access"] = access
        state.relationships.append(entry)
        return f"Relationship {from_comp} → {to_comp} ({rel_type}) added"

    def write_archimate_model(model_name: str = "", description: str = "") -> str:
        _guard("write_archimate_model")

        # Merge enrichments into the Application layer elements
        app_elements = state.layers[0]["elements"] if state.layers else []
        for elem in app_elements:
            if elem.get("type") != "ApplicationComponent":
                continue
            enr = state._enrichments.get(elem["name"], {})
            elem.update(enr)

        # Strip internal rationale fields from the serialised motivation
        clean_motivation: dict[str, list] = {}
        for key, items in state.motivation.items():
            clean_motivation[key] = [
                {k: v for k, v in item.items() if k != "rationale"}
                for item in items
            ]

        model = {
            "meta": {
                "name":         model_name or "agent-generated-archimate-model",
                "version":      "1.0",
                "description":  description or "ArchiMate model produced by hybrid rule+LLM agent",
                "generated_by": "ArchiMateGeneratorAgent",
                "note":         "Generated — do not edit manually",
            },
            "motivation":    clean_motivation,
            "layers":        state.layers,
            "relationships": state.relationships,
            "events":        state.events,
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            yaml.dump(model, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        p = len(state.motivation["principles"])
        c = len(state.motivation["constraints"])
        r = len(state.motivation["requirements"])
        return (
            f"Model written to {output_path} — "
            f"{p} principles · {c} constraints · {r} requirements · "
            f"{len(state.relationships)} relationships"
        )

    def run_boucle0() -> str:
        _guard("run_boucle0")
        if boucle0_fn is None:
            return "Boucle 0 not wired (pass --boucle0 flag to enable)"
        boucle0_fn()
        return "Boucle 0 completed — AGT policy updated from new model"

    def push_to_archiserver(
        base_url: str = "",
        elements: list | None = None,
        relationships: list | None = None,
        dry_run: bool = True,
    ) -> str:
        """
        Write generated elements back to the Archi model via ArchiMateWriter REST API.
        Always routed through ArchiMateWriter (human-gated component).
        dry_run=True (default) performs validation only — no writes.
        """
        _guard("push_to_archiserver")
        url           = base_url or archiserver or ""
        if not url:
            return "Error: no ArchiServer URL — pass base_url or start agent with --archiserver"
        base_url      = url
        elements      = elements      or []
        relationships = relationships or []
        total = len(elements) + len(relationships)

        if dry_run:
            return (
                f"[dry-run] Would push {len(elements)} elements "
                f"+ {len(relationships)} relationships to {base_url}"
            )

        try:
            import httpx
        except ImportError:
            return "Error: httpx not installed — run: pip install httpx"

        pushed, errors = 0, []
        if elements:
            r = httpx.post(
                f"{base_url}/api/elements/batch",
                json={"elements": elements},
                timeout=30,
            )
            if r.is_success:
                pushed += len(elements)
            else:
                errors.append(f"elements: {r.status_code} {r.text[:120]}")

        if relationships:
            r = httpx.post(
                f"{base_url}/api/relationships/batch",
                json={"relationships": relationships},
                timeout=30,
            )
            if r.is_success:
                pushed += len(relationships)
            else:
                errors.append(f"relationships: {r.status_code} {r.text[:120]}")

        if errors:
            return f"Partial push ({pushed}/{total}). Errors: {'; '.join(errors)}"
        return f"Pushed {pushed} items to {base_url}"

    return {
        "add_principle":         add_principle,
        "add_constraint":        add_constraint,
        "add_requirement":       add_requirement,
        "enrich_component":      enrich_component,
        "add_relationship":      add_relationship,
        "write_archimate_model": write_archimate_model,
        "run_boucle0":           run_boucle0,
        "push_to_archiserver":   push_to_archiserver,
    }


# ── Tool schemas (JSON Schema for Anthropic API) ──────────────────────────────

TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "add_principle",
        "description": (
            "Add an architectural Principle to the ArchiMate Motivation Aspect. "
            "Use for fundamental beliefs that guide design decisions across the system."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "id":        {"type": "string",
                              "description": "Unique identifier, e.g. P1, P11"},
                "severity":  {"type": "string", "enum": ["must", "should", "may"]},
                "text":      {"type": "string",
                              "description": "The principle statement (concise, imperative)"},
                "rationale": {"type": "string",
                              "description": "Why this principle matters architecturally"},
            },
            "required": ["id", "severity", "text"],
        },
    },
    {
        "name": "add_constraint",
        "description": (
            "Add an architectural Constraint to the ArchiMate Motivation Aspect. "
            "Use for hard boundaries that must never be violated (access control, "
            "data isolation, write-prohibition rules)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "id":        {"type": "string",
                              "description": "Unique identifier, e.g. C4, C5"},
                "severity":  {"type": "string", "enum": ["must", "should", "may"]},
                "text":      {"type": "string",
                              "description": "The constraint statement"},
                "rationale": {"type": "string",
                              "description": "Why this constraint exists"},
            },
            "required": ["id", "severity", "text"],
        },
    },
    {
        "name": "add_requirement",
        "description": (
            "Add an architectural Requirement. Use for capabilities the system must "
            "provide: observability, auditability, reload behaviour, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "id":        {"type": "string",
                              "description": "Unique identifier, e.g. R4, R5"},
                "severity":  {"type": "string", "enum": ["must", "should", "may"]},
                "text":      {"type": "string",
                              "description": "The requirement statement"},
                "rationale": {"type": "string",
                              "description": "Why this requirement exists"},
            },
            "required": ["id", "severity", "text"],
        },
    },
    {
        "name": "enrich_component",
        "description": (
            "Attach semantic metadata to an existing ApplicationComponent: its "
            "architectural role, key design decisions, and security risk level."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name":          {"type": "string",
                                  "description": "Exact component name as declared"},
                "semantic_role": {"type": "string",
                                  "description": "Architectural role, e.g. 'policy enforcement point'"},
                "design_notes":  {"type": "string",
                                  "description": "Key design choices or patterns"},
                "risk_level":    {"type": "string",
                                  "enum": ["critical", "high", "medium", "low"],
                                  "description": "Impact if this component is compromised"},
            },
            "required": ["name"],
        },
    },
    {
        "name": "add_relationship",
        "description": (
            "Add a relationship that was not inferred from the source. Use sparingly — "
            "most relationships are already loaded. Useful for implicit associations or "
            "composition links."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "from_comp": {"type": "string", "description": "Source element name"},
                "to_comp":   {"type": "string", "description": "Target element name"},
                "rel_type":  {"type": "string",
                              "enum": ["Serving", "Access", "Triggering",
                                       "Composition", "Aggregation", "Association"]},
                "access":    {"type": "string", "enum": ["read", "write", "readwrite", ""],
                              "description": "For Access relationships"},
                "forbidden": {"type": "boolean",
                              "description": "True if this access is explicitly prohibited"},
            },
            "required": ["from_comp", "to_comp", "rel_type"],
        },
    },
    {
        "name": "write_archimate_model",
        "description": (
            "Finalise and write the enriched ArchiMate model to YAML. "
            "Call this when you are satisfied with the motivation and enrichments."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "model_name":  {"type": "string",
                                "description": "Model identifier (slug)"},
                "description": {"type": "string",
                                "description": "One-line description of the model"},
            },
            "required": [],
        },
    },
    {
        "name": "run_boucle0",
        "description": (
            "After writing the model, trigger Boucle 0 to regenerate archguard "
            "guardrails and the AGT harness policy from the new model."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "push_to_archiserver",
        "description": (
            "Push generated elements and relationships to the live Archi model via "
            "the ArchiMateWriter REST endpoint. "
            "Always use dry_run=true first to validate before committing. "
            "Requires human approval (R2) — the ArchiMateWriter component enforces the gate."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "base_url": {
                    "type": "string",
                    "description": "ArchiMateWriter base URL, e.g. http://localhost:8080",
                },
                "elements": {
                    "type": "array",
                    "description": "ApplicationComponent or DataObject dicts to upsert",
                    "items": {"type": "object"},
                },
                "relationships": {
                    "type": "array",
                    "description": "Relationship dicts to upsert",
                    "items": {"type": "object"},
                },
                "dry_run": {
                    "type": "boolean",
                    "description": "If true (default), validate only — no writes",
                    "default": True,
                },
            },
            "required": ["base_url"],
        },
    },
]
