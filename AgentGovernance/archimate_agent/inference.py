"""
Structural inference layer — rule-based extraction of ArchiMate elements
from Python component metadata (components.py format).

No LLM is involved here. This produces the structural skeleton that the
agent then enriches semantically.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


def _load_module(source_path: Path) -> Any:
    name = "_archimate_source"
    spec = importlib.util.spec_from_file_location(name, source_path)
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can find the module in sys.modules
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    finally:
        sys.modules.pop(name, None)
    return module


def build_skeleton(source_path: Path) -> dict[str, Any]:
    """
    Infer the structural ArchiMate skeleton from a components.py file.

    Returns a dict with:
      - layers: ApplicationComponent + DataObject elements
      - relationships: Serving / Access / Triggering
      - motivation: existing Principle / Constraint / Requirement elements
      - events: event names
      - components_summary: flat list for the LLM prompt
    """
    module = _load_module(source_path)

    components   = getattr(module, "COMPONENTS", [])
    data_objects = getattr(module, "DATA_OBJECTS", [])
    motivation   = getattr(module, "MOTIVATION", [])
    events       = getattr(module, "EVENTS", [])

    # ── Application layer elements ────────────────────────────────────────────
    elements: list[dict] = []
    for comp in components:
        entry: dict[str, Any] = {
            "name": comp.name,
            "type": "ApplicationComponent",
            "description": comp.description,
        }
        if comp.functions:
            entry["functions"] = comp.functions
        elements.append(entry)

    for obj in data_objects:
        entry = {"name": obj.name, "type": "DataObject"}
        if obj.description:
            entry["description"] = obj.description
        elements.append(entry)

    # ── Relationships ─────────────────────────────────────────────────────────
    relationships: list[dict] = []
    for comp in components:
        for target in comp.serves:
            relationships.append(
                {"from": comp.name, "to": target, "type": "Serving", "forbidden": False}
            )
        for target in comp.reads:
            relationships.append(
                {"from": comp.name, "to": target,
                 "type": "Access", "access": "read", "forbidden": False}
            )
        for target in comp.writes:
            relationships.append(
                {"from": comp.name, "to": target,
                 "type": "Access", "access": "write", "forbidden": False}
            )
        for target in comp.forbidden_writes:
            relationships.append(
                {"from": comp.name, "to": target,
                 "type": "Access", "access": "write", "forbidden": True}
            )
        for event in comp.triggers:
            relationships.append(
                {"from": comp.name, "to": event, "type": "Triggering"}
            )

    # ── Motivation (from source declarations) ─────────────────────────────────
    key_map = {
        "Principle":   "principles",
        "Constraint":  "constraints",
        "Requirement": "requirements",
    }
    motivation_dict: dict[str, list] = {
        "principles": [], "constraints": [], "requirements": []
    }
    for elem in motivation:
        motivation_dict[key_map[elem.type]].append(
            {"id": elem.id, "severity": elem.severity, "text": elem.text}
        )

    # ── Flat summary for LLM prompt ───────────────────────────────────────────
    components_summary = [
        {
            "name":            c.name,
            "description":     c.description,
            "functions":       c.functions,
            "serves":          c.serves,
            "reads":           c.reads,
            "writes":          c.writes,
            "forbidden_writes": c.forbidden_writes,
        }
        for c in components
    ]

    return {
        "layers":             [{"name": "Application", "elements": elements}],
        "relationships":      relationships,
        "motivation":         motivation_dict,
        "events":             events,
        "components_summary": components_summary,
    }
