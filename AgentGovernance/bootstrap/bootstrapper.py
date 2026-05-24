"""
ModelBootstrapper — generates bootstrap_model.yaml from component metadata.

The Harness describes itself: component declarations in components.py
are the single source of truth. The YAML is always generated, never
edited by hand.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .components import COMPONENTS, DATA_OBJECTS, EVENTS, MOTIVATION


class ModelBootstrapper:
    """
    Inspects Harness component metadata and writes bootstrap_model.yaml.

    The generated file is the ArchiMate model of the Harness itself.
    Boucle 0 reads this file to produce the AGT policy that governs
    the Harness at runtime.
    """

    def __init__(self, output_path: str | Path | None = None) -> None:
        default = Path(__file__).parent / "generated" / "bootstrap_model.yaml"
        self.output_path = Path(output_path) if output_path else default

    def generate(self) -> dict[str, Any]:
        """Build and write the bootstrap model. Returns the model dict."""
        model = {
            "meta": {
                "name": "harness-bootstrap-model",
                "version": "1.0",
                "description": "Self-describing ArchiMate model of the Governance Harness",
                "generated_by": "ModelBootstrapper",
                "note": "Generated from components.py — do not edit manually",
            },
            "motivation": self._build_motivation(),
            "layers":     self._build_layers(),
            "relationships": self._build_relationships(),
            "events": EVENTS,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            yaml.dump(model, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        return model

    # ── private builders ──────────────────────────────────────────────────────

    def _build_motivation(self) -> dict[str, list]:
        result: dict[str, list] = {"principles": [], "constraints": [], "requirements": []}
        key_map = {"Principle": "principles", "Constraint": "constraints", "Requirement": "requirements"}
        for elem in MOTIVATION:
            result[key_map[elem.type]].append({
                "id": elem.id,
                "severity": elem.severity,
                "text": elem.text,
            })
        return result

    def _build_layers(self) -> list[dict]:
        elements: list[dict] = []
        for comp in COMPONENTS:
            entry: dict[str, Any] = {
                "name": comp.name,
                "type": "ApplicationComponent",
                "description": comp.description,
            }
            if comp.functions:
                entry["functions"] = comp.functions
            elements.append(entry)
        for obj in DATA_OBJECTS:
            entry = {"name": obj.name, "type": "DataObject"}
            if obj.description:
                entry["description"] = obj.description
            elements.append(entry)
        return [{"name": "Application", "elements": elements}]

    def _build_relationships(self) -> list[dict]:
        rels: list[dict] = []
        for comp in COMPONENTS:
            for target in comp.serves:
                rels.append({"from": comp.name, "to": target,
                             "type": "Serving", "forbidden": False})
            for target in comp.reads:
                rels.append({"from": comp.name, "to": target,
                             "type": "Access", "access": "read", "forbidden": False})
            for target in comp.writes:
                rels.append({"from": comp.name, "to": target,
                             "type": "Access", "access": "write", "forbidden": False})
            for target in comp.forbidden_writes:
                rels.append({"from": comp.name, "to": target,
                             "type": "Access", "access": "write", "forbidden": True})
            for event in comp.triggers:
                rels.append({"from": comp.name, "to": event,
                             "type": "Triggering"})
        return rels

    # ── stats ─────────────────────────────────────────────────────────────────

    def stats(self, model: dict[str, Any]) -> dict[str, int]:
        mot = model["motivation"]
        return {
            "components": sum(
                1 for e in model["layers"][0]["elements"]
                if e["type"] == "ApplicationComponent"
            ),
            "data_objects": sum(
                1 for e in model["layers"][0]["elements"]
                if e["type"] == "DataObject"
            ),
            "principles":   len(mot["principles"]),
            "constraints":  len(mot["constraints"]),
            "requirements": len(mot["requirements"]),
            "relationships": len(model["relationships"]),
            "forbidden":    sum(1 for r in model["relationships"] if r.get("forbidden")),
        }
