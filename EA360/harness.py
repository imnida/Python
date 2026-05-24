"""
LLM-ready harness tools for EA360.

Each function is designed to score >= 0.7 on tool_readiness_score.py:
typed parameters, USE WHEN / NEVER USE sections, Args/Returns docs,
and domain vocabulary aligned with TOGAF 10 / ArchiMate 3.2.

The module exposes TOOLS (list of Anthropic-compatible tool dicts)
and HANDLERS (dispatch map from tool name → callable) for use in
the agent loop.
"""

from __future__ import annotations

import json
from typing import Any, Literal

from .metamodel import EA360, ElementType, Lifecycle, RelationshipType

# Singleton model instance shared across a session
_model = EA360()


def reset_model() -> None:
    """Replace the session model with a fresh EA360 instance."""
    global _model
    _model = EA360()


# ---------------------------------------------------------------------------
# Tool functions
# ---------------------------------------------------------------------------

def create_element(
    name: str,
    element_type: Literal[
        "BusinessProcess", "BusinessFunction", "BusinessRole", "BusinessObject",
        "ApplicationComponent", "ApplicationService", "ApplicationInterface",
        "DataObject", "DataStore", "Node", "InfrastructureService",
    ],
    properties: dict[str, Any],
) -> dict[str, Any]:
    """
    Create and persist a new ArchiMate 3.2 element in the EA360 model.

    USE WHEN: The user explicitly asks to add an architecture element
    (component, process, data object, node, etc.) to the current model,
    after confirming its ArchiMate layer and required TOGAF properties.

    NEVER USE FOR: Temporary sketches, elements without a clear TOGAF
    layer assignment, or before the user has confirmed the stakeholder
    context and compliance obligations.

    Args:
        name: Human-readable identifier, unique within its ArchiMate layer.
        element_type: ArchiMate 3.2 concept class. Determines mandatory
            properties:
            - DataObject requires { "sensitivity": "public|internal|confidential",
              "owner": str }
            - ApplicationComponent requires { "technology": str }
            - BusinessProcess requires { "process_owner": str }
        properties: Domain-specific metadata dict (see per-type requirements above).

    Returns:
        dict: {
            "id": str,           # UUID of the created element
            "name": str,
            "status": "created",
            "warnings": list[str]  # TOGAF compliance warnings, empty if compliant
        }
    """
    elem = _model.add_component(name=name, type=element_type, properties=properties)
    warnings = elem.validate()
    return {"id": elem.id, "name": elem.name, "status": "created", "warnings": warnings}


def link_relationship(
    source_name: str,
    target_name: str,
    relationship_type: Literal[
        "serves", "realizes", "assigned_to", "composed_of", "aggregates",
        "used_by", "triggers", "associated_with", "complies_with", "influences",
    ],
) -> dict[str, Any]:
    """
    Create a typed ArchiMate 3.2 relationship between two existing elements.

    USE WHEN: The user wants to express a structural or behavioural
    dependency between two elements already present in the EA360 model.
    Use the ArchiMate relationship type that best captures the TOGAF
    semantics (e.g. 'realizes' for an ApplicationComponent implementing
    a BusinessProcess; 'serves' for a service exposing functionality).

    NEVER USE FOR: Linking elements that do not yet exist in the model —
    call create_element first. Do not use 'associated_with' as a catch-all;
    prefer the most specific type available.

    Args:
        source_name: Name of the source element (must already exist in model).
        target_name: Name of the target element (must already exist in model).
        relationship_type: ArchiMate 3.2 relationship concept.

    Returns:
        dict: {
            "id": str,           # UUID of the created relationship
            "source": str,       # source element name
            "target": str,       # target element name
            "type": str,
            "status": "created" | "error",
            "error": str | None
        }
    """
    source = _model.find_by_name(source_name)
    target = _model.find_by_name(target_name)
    if source is None:
        return {"status": "error", "error": f"Element '{source_name}' not found"}
    if target is None:
        return {"status": "error", "error": f"Element '{target_name}' not found"}
    rel = _model.link(source.id, target.id, relationship_type)
    return {
        "id": rel.id,
        "source": source_name,
        "target": target_name,
        "type": rel.type.value,
        "status": "created",
        "error": None,
    }


def validate_togaf() -> dict[str, Any]:
    """
    Run TOGAF 10 compliance checks on the current EA360 model.

    USE WHEN: The user asks to validate the architecture, check conformance,
    or before exporting artefacts. Also call this after a batch of
    create_element / link_relationship calls to surface issues early.

    NEVER USE FOR: Individual element checks — this validates the full model.
    Do not call on an empty model (the result will be trivially compliant
    but uninformative).

    Args: (none)

    Returns:
        dict: {
            "compliant": bool,
            "issue_count": int,
            "issues": {
                "<element_id>": list[str]  # one string per TOGAF violation
            }
        }
    """
    issues = _model.validate()
    return {
        "compliant": len(issues) == 0,
        "issue_count": sum(len(v) for v in issues.values()),
        "issues": issues,
    }


def update_lifecycle(
    element_name: str,
    new_state: Literal["draft", "validated", "deprecated", "archived"],
) -> dict[str, Any]:
    """
    Advance or revert an ArchiMate element's governance lifecycle state.

    USE WHEN: The user confirms that an element has passed a governance gate
    (e.g. ADR review, stakeholder sign-off) and should move from 'draft' to
    'validated', or that an element is being phased out ('deprecated' →
    'archived'). Document the rationale in the audit trail before calling.

    NEVER USE FOR: Skipping lifecycle stages without governance approval,
    or archiving elements that still have active TOGAF relationships.

    Args:
        element_name: Name of the element whose lifecycle state will change.
        new_state: Target lifecycle state. Valid transitions:
            draft → validated → deprecated → archived

    Returns:
        dict: {
            "id": str,
            "name": str,
            "previous_state": str,
            "new_state": str,
            "status": "updated" | "error",
            "error": str | None
        }
    """
    elem = _model.find_by_name(element_name)
    if elem is None:
        return {"status": "error", "error": f"Element '{element_name}' not found"}
    previous = elem.lifecycle.value
    elem.lifecycle = Lifecycle(new_state)
    return {
        "id": elem.id,
        "name": elem.name,
        "previous_state": previous,
        "new_state": new_state,
        "status": "updated",
        "error": None,
    }


def export_model(format: Literal["json", "summary"]) -> dict[str, Any]:
    """
    Export the current EA360 model in the requested format.

    USE WHEN: The user asks to save, share, or review the architecture model.
    Use 'json' for machine-readable output (CI/CD, version control),
    'summary' for a human-readable overview suitable for stakeholder review.

    NEVER USE FOR: Exporting a model that has not been validated — call
    validate_togaf first and resolve P0 issues before exporting.

    Args:
        format: Output format.
            - "json": Full serialisation of all ArchiMate elements and
              relationships as a dict (can be written to architecture.json).
            - "summary": Counts and names grouped by ArchiMate layer.

    Returns:
        dict: {
            "format": str,
            "content": dict | str   # dict for json, str for summary
        }
    """
    if format == "json":
        return {"format": "json", "content": _model.to_dict()}

    data = _model.to_dict()
    by_type: dict[str, list[str]] = {}
    for elem in data["elements"]:
        by_type.setdefault(elem["type"], []).append(elem["name"])
    lines = [f"EA360 Model — {len(data['elements'])} elements, "
             f"{len(data['relationships'])} relationships"]
    for etype, names in sorted(by_type.items()):
        lines.append(f"  {etype} ({len(names)}): {', '.join(names)}")
    return {"format": "summary", "content": "\n".join(lines)}


# ---------------------------------------------------------------------------
# Anthropic-compatible tool manifests + dispatch map
# ---------------------------------------------------------------------------

TOOLS: list[dict[str, Any]] = [
    {
        "name": "create_element",
        "description": (
            "Create a new ArchiMate 3.2 element (Business/Application/Data/Technology "
            "layer) in the EA360 TOGAF-compliant architecture model."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "element_type": {
                    "type": "string",
                    "enum": [e.value for e in ElementType],
                },
                "properties": {"type": "object"},
            },
            "required": ["name", "element_type", "properties"],
        },
    },
    {
        "name": "link_relationship",
        "description": (
            "Create a typed ArchiMate 3.2 relationship between two existing "
            "elements in the EA360 model."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "source_name": {"type": "string"},
                "target_name": {"type": "string"},
                "relationship_type": {
                    "type": "string",
                    "enum": [r.value for r in RelationshipType],
                },
            },
            "required": ["source_name", "target_name", "relationship_type"],
        },
    },
    {
        "name": "validate_togaf",
        "description": "Run TOGAF 10 compliance checks on the full EA360 model.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "update_lifecycle",
        "description": (
            "Advance an ArchiMate element's governance lifecycle state "
            "(draft → validated → deprecated → archived)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "element_name": {"type": "string"},
                "new_state": {
                    "type": "string",
                    "enum": [s.value for s in Lifecycle],
                },
            },
            "required": ["element_name", "new_state"],
        },
    },
    {
        "name": "export_model",
        "description": (
            "Export the current EA360 architecture model as JSON "
            "(machine-readable) or summary (stakeholder review)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "format": {"type": "string", "enum": ["json", "summary"]},
            },
            "required": ["format"],
        },
    },
]

HANDLERS: dict[str, Any] = {
    "create_element": create_element,
    "link_relationship": link_relationship,
    "validate_togaf": validate_togaf,
    "update_lifecycle": update_lifecycle,
    "export_model": export_model,
}
