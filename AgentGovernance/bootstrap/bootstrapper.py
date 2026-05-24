"""
ModelBootstrapper — generates a bootstrap_model.yaml from component metadata.

Accepts either:
  - the built-in harness components (default, no components_path)
  - any components_*.py file passed via components_path

Supports multi-layer models: Business, Application, Implementation.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

import yaml

# Default harness import (used when components_path is None)
from .components import COMPONENTS  as _H_COMPONENTS
from .components import DATA_OBJECTS as _H_DATA_OBJECTS
from .components import EVENTS       as _H_EVENTS
from .components import MOTIVATION   as _H_MOTIVATION


class ModelBootstrapper:
    """
    Inspects component metadata and writes a bootstrap_model.yaml.

    The generated file is the ArchiMate model of the described system.
    Boucle 0 reads this file to produce the AGT policy.
    """

    def __init__(
        self,
        output_path:     str | Path | None = None,
        components_path: str | Path | None = None,
    ) -> None:
        default = Path(__file__).parent / "generated" / "bootstrap_model.yaml"
        self.output_path = Path(output_path) if output_path else default

        if components_path:
            self._load_from_path(Path(components_path))
        else:
            self._components     = _H_COMPONENTS
            self._data_objects   = _H_DATA_OBJECTS
            self._events         = _H_EVENTS
            self._motivation     = _H_MOTIVATION
            self._business_roles = []
            self._artifacts      = []

    # ── dynamic loader ────────────────────────────────────────────────────────

    def _load_from_path(self, path: Path) -> None:
        name = "_bootstrap_source"
        spec = importlib.util.spec_from_file_location(name, path)
        mod  = importlib.util.module_from_spec(spec)
        # Allow relative imports (e.g. from .components import ...) by
        # declaring the module as belonging to the bootstrap package.
        mod.__package__ = __package__  # "AgentGovernance.bootstrap"
        sys.modules[name] = mod
        try:
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
        finally:
            sys.modules.pop(name, None)

        self._components     = getattr(mod, "COMPONENTS",     [])
        self._data_objects   = getattr(mod, "DATA_OBJECTS",   [])
        self._events         = getattr(mod, "EVENTS",         [])
        self._motivation     = getattr(mod, "MOTIVATION",     [])
        self._business_roles = getattr(mod, "BUSINESS_ROLES", [])
        self._artifacts      = getattr(mod, "ARTIFACTS",      [])

    # ── public API ────────────────────────────────────────────────────────────

    def generate(self) -> dict[str, Any]:
        """Build and write the bootstrap model. Returns the model dict."""
        model = {
            "meta": {
                "name":         "harness-bootstrap-model",
                "version":      "1.0",
                "description":  "Self-describing ArchiMate model of the system",
                "generated_by": "ModelBootstrapper",
                "note":         "Generated from components — do not edit manually",
            },
            "motivation":    self._build_motivation(),
            "layers":        self._build_layers(),
            "relationships": self._build_relationships(),
            "events":        self._events,
        }
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(
            yaml.dump(model, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        return model

    # ── private builders ──────────────────────────────────────────────────────

    def _build_motivation(self) -> dict[str, list]:
        result: dict[str, list] = {
            "principles": [], "constraints": [], "requirements": [],
        }
        key_map = {
            "Principle":   "principles",
            "Constraint":  "constraints",
            "Requirement": "requirements",
        }
        for elem in self._motivation:
            key = key_map.get(elem.type)
            if key:
                result[key].append(
                    {"id": elem.id, "severity": elem.severity, "text": elem.text}
                )
        return result

    def _build_layers(self) -> list[dict]:
        layers: list[dict] = []

        # Business layer — only when BusinessRoles are declared
        if self._business_roles:
            biz_elements = []
            for r in self._business_roles:
                entry: dict[str, Any] = {
                    "name": r.name, "type": "BusinessRole",
                }
                if r.description:
                    entry["description"] = r.description
                if r.assigned_to:
                    entry["assigned_to"] = r.assigned_to
                biz_elements.append(entry)
            layers.append({"name": "Business", "elements": biz_elements})

        # Application layer — components + data objects
        app_elements: list[dict] = []
        for comp in self._components:
            entry = {
                "name": comp.name,
                "type": "ApplicationComponent",
                "description": comp.description,
            }
            if comp.functions:
                entry["functions"] = comp.functions
            if comp.gate_review:
                entry["gate_review"] = comp.gate_review
            app_elements.append(entry)

        for obj in self._data_objects:
            entry = {"name": obj.name, "type": "DataObject"}
            if obj.description:
                entry["description"] = obj.description
            app_elements.append(entry)

        layers.append({"name": "Application", "elements": app_elements})

        # Implementation layer — ArchitectureArtifacts
        if self._artifacts:
            impl_elements = []
            for a in self._artifacts:
                entry = {"name": a.name, "type": a.artifact_type}
                if a.description:
                    entry["description"] = a.description
                impl_elements.append(entry)
            layers.append({"name": "Implementation", "elements": impl_elements})

        return layers

    def _build_relationships(self) -> list[dict]:
        rels: list[dict] = []

        for comp in self._components:
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
            for prev in comp.preceded_by:
                rels.append({"from": prev, "to": comp.name,
                             "type": "Flow"})
            if comp.gate_review:
                rels.append({"from": comp.name, "to": comp.gate_review,
                             "type": "Association", "role": "gate-review"})

        for role in self._business_roles:
            for target in role.assigned_to:
                rels.append({"from": role.name, "to": target,
                             "type": "Assignment"})

        return rels

    # ── stats ─────────────────────────────────────────────────────────────────

    def stats(self, model: dict[str, Any]) -> dict[str, int]:
        mot = model["motivation"]
        all_elements = [
            e for layer in model["layers"] for e in layer["elements"]
        ]
        return {
            "components": sum(
                1 for e in all_elements if e["type"] == "ApplicationComponent"
            ),
            "data_objects": sum(
                1 for e in all_elements if e["type"] == "DataObject"
            ),
            "business_roles": sum(
                1 for e in all_elements if e["type"] == "BusinessRole"
            ),
            "artifacts": sum(
                1 for e in all_elements
                if e["type"] in ("Deliverable", "WorkPackage", "Plateau")
            ),
            "principles":    len(mot["principles"]),
            "constraints":   len(mot["constraints"]),
            "requirements":  len(mot["requirements"]),
            "relationships": len(model["relationships"]),
            "forbidden":     sum(
                1 for r in model["relationships"] if r.get("forbidden")
            ),
        }
